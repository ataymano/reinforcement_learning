#include <boost/uuid/random_generator.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <thread>

#include "live_model.h"
#include "rl_sim_cpp.h"
#include "person.h"
#include "simulation_stats.h"
#include "constants.h"

using namespace std;

std::string get_dist_str(const reinforcement_learning::ranking_response& response);

int rl_sim::loop() {
  if ( !init() ) return -1;
  const auto is_cb = !_options["cb_json_config"].as<std::string>().empty();
  const auto is_ccb = !_options["ccb_json_config"].as<std::string>().empty();
  if(is_ccb & !is_cb)
  {
    return ccb_loop();
  }
  else if (is_cb && !is_ccb){
    return cb_loop();
  }
  else {
    return cb_vs_ccb_loop();
  }
}

int rl_sim::cb_loop() {
  r::ranking_response response;
  simulation_stats stats;
  std::vector<bool> included_topics(_topics.size(), true);
  std::vector<size_t> original_ids(_topics.size());
  while ( _run_loop ) {
    auto& p = pick_a_random_person();
    const auto context_features = p.get_features();
    const auto action_features = get_action_features(included_topics, original_ids);
    const auto context_json = create_context_json(context_features,action_features);
    const auto req_id = create_event_id();
    r::api_status status;

    // Choose an action
    if ( _rl_cb->choose_rank(req_id.c_str(), context_json.c_str(), response, &status) != err::success ) {
      std::cout << status.get_error_msg() << std::endl;
      continue;
    }

    // Use the chosen action
    size_t chosen_action;
    if ( response.get_chosen_action_id(chosen_action) != err::success ) {
      std::cout << status.get_error_msg() << std::endl;
      continue;
    }

    // What outcome did this action get?
    const auto outcome = p.get_outcome(_topics[chosen_action]);

    // Report outcome received
    if ( _rl_cb->report_outcome(req_id.c_str(), outcome, &status) != err::success && outcome > 0.00001f ) {
      std::cout << status.get_error_msg() << std::endl;
      continue;
    }

    stats.record(p.id(), chosen_action, outcome);

    std::cout << " " << stats.count() << ", ctxt, " << p.id() << ", action, " << chosen_action << ", outcome, " << outcome
      << ", dist, " << get_dist_str(response) << ", " << stats.get_stats(p.id(), chosen_action) << std::endl;

    std::this_thread::sleep_for(std::chrono::milliseconds(2000));
  }

  return 0;
}

int rl_sim::ccb_loop() {
  r::decision_response decision;
  simulation_stats stats;
  std::vector<bool> included_topics(_topics.size(), true);
  std::vector<size_t> original_ids(_topics.size());
  while ( _run_loop ) {
    auto& p = pick_a_random_person();
    const auto context_features = p.get_features();
    const auto action_features = get_action_features(included_topics, original_ids);

    std::vector<std::string> ids;
    for(int i = 0; i < NUM_SLOTS; i++)
    {
      ids.push_back(create_event_id());
    }

    const auto slot_json =  get_slot_features(ids);
    const auto context_json = create_context_json(context_features,action_features, slot_json);
    std::cout << context_json <<std::endl;
    r::api_status status;

    // Choose an action
    if ( _rl_ccb->request_decision(context_json.c_str(), decision, &status) != err::success ) {
      std::cout << status.get_error_msg() << std::endl;
      continue;
    }

    auto index = 0;
    for(auto& response : decision)
    {
      size_t chosen_action;
      if ( response.get_chosen_action_id(chosen_action) != err::success ) {
        std::cout << status.get_error_msg() << std::endl;
        continue;
      }

      const auto outcome = p.get_outcome(_topics[chosen_action]);

      // Report outcome received
      if ( _rl_ccb->report_outcome(ids[index].c_str(), outcome, &status) != err::success && outcome > 0.00001f ) {
        std::cout << status.get_error_msg() << std::endl;
        continue;
      }

      stats.record(p.id(), chosen_action, outcome);

      std::cout << " " << stats.count() << ", ctxt, " << p.id() << ", action, " << chosen_action << ", slot, " << index << ", outcome, " << outcome
        << ", dist, " << get_dist_str(response) << ", " << stats.get_stats(p.id(), chosen_action) << std::endl;
      index++;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(2000));
  }

  return 0;
}

int rl_sim::cb_vs_ccb_loop() {
	r::decision_response decision;
	r::ranking_response response;
	simulation_stats cb_stats, ccb_stats;
	std::vector<size_t> original_ids_ccb(_topics.size());
	while (_run_loop) {
		std::vector<bool> included_topics(_topics.size(), true);
		auto& p = pick_a_random_person();
		const auto context_features = p.get_features();
		auto action_features = get_action_features(included_topics, original_ids_ccb);

		//ccb part
		std::vector<std::string> ids;
		for (int i = 0; i < NUM_SLOTS; i++)
		{
			ids.push_back(create_event_id());
		}

		const auto slot_json = get_slot_features(ids);
		const auto context_json = create_context_json(context_features, action_features, slot_json);
		std::cout << context_json << std::endl;
		r::api_status status;

		// Choose an action
		if (_rl_ccb->request_decision(context_json.c_str(), decision, &status) != err::success) {
			std::cout << status.get_error_msg() << std::endl;
			continue;
		}

		auto index = 0;
		for (auto& response : decision)
		{
			size_t chosen_action;
			if (response.get_chosen_action_id(chosen_action) != err::success) {
				std::cout << status.get_error_msg() << std::endl;
				continue;
			}

			const auto outcome = p.get_outcome(_topics[chosen_action]);

			// Report outcome received
			if (_rl_ccb->report_outcome(ids[index].c_str(), outcome, &status) != err::success && outcome > 0.00001f) {
				std::cout << status.get_error_msg() << std::endl;
				continue;
			}
			included_topics[chosen_action] = false;
			ccb_stats.record(p.id(), chosen_action, outcome);
			std::cout << "CCB" << std::endl;
			std::cout << " " << ccb_stats.count() << ", ctxt, " << p.id() << ", action, " << chosen_action << ", slot, " << index << ", outcome, " << outcome
				<< ", dist, " << get_dist_str(response) << ", " << ccb_stats.get_stats(p.id(), chosen_action) << std::endl;
			index++;
		}
		std::cout << "Not chosen:" << std::endl;
		for (size_t i = 0; i < _topics.size(); ++i) {
			if (included_topics[i]) {
				std::cout << "action, " << i << ", " << ccb_stats.get_stats(p.id(), i) << std::endl;
			}
		}

		//cb part
		included_topics.assign(_topics.size(), true);
		std::vector<size_t> original_ids(_topics.size());
		for (size_t i = 0; i < _topics.size(); ++i) original_ids[i] = i;
		for (int i = 0; i < NUM_SLOTS; i++)
		{
			const auto cb_context_json = create_context_json(context_features, action_features);
			if (_rl_cb->choose_rank(ids[i].c_str(), cb_context_json.c_str(), response, &status) != err::success) {
				std::cout << status.get_error_msg() << std::endl;
				continue;
			}

			// Use the chosen action
			size_t chosen_action;
			if (response.get_chosen_action_id(chosen_action) != err::success) {
				std::cout << status.get_error_msg() << std::endl;
				continue;
			}
			chosen_action = original_ids[chosen_action];
			included_topics[chosen_action] = false;
			// What outcome did this action get?
			const auto outcome = p.get_outcome(_topics[chosen_action]);

			// Report outcome received
			if (_rl_cb->report_outcome(ids[i].c_str(), outcome, &status) != err::success && outcome > 0.00001f) {
				std::cout << status.get_error_msg() << std::endl;
				continue;
			}

			cb_stats.record(p.id(), chosen_action, outcome);
			std::cout << std::endl << "CB" << std::endl;
			std::cout << " " << cb_stats.count() << ", ctxt, " << p.id() << ", action, " << chosen_action << ", outcome, " << outcome
				<< ", dist, " << get_dist_str(response) << ", " << cb_stats.get_stats(p.id(), chosen_action) << std::endl;
			original_ids.resize(_topics.size() - i - 1);
			action_features = get_action_features(included_topics, original_ids);
		}
		std::cout << "Not chosen:" << std::endl;
		for (size_t i = 0; i < _topics.size(); ++i) {
			if (included_topics[i]) {
				std::cout << "action, " << i << ", " << ccb_stats.get_stats(p.id(), i) << std::endl;
			}
		}

		std::cout << std::endl << std::endl;

	//	std::this_thread::sleep_for(std::chrono::milliseconds(2000));
	}

	return 0;
}

person& rl_sim::pick_a_random_person() {
  return _people[rand() % _people.size()];
}

int rl_sim::load_config_from_json(  const std::string& file_name,
                                    u::configuration& config,
                                    r::api_status* status) {
  std::string config_str;

  // Load contents of config file into a string
  RETURN_IF_FAIL(load_file(file_name, config_str));

  // Use library supplied convenience method to parse json and build config object
  return cfg::create_from_json(config_str, config, nullptr, status);
}

int rl_sim::load_file(const std::string& file_name, std::string& config_str) {
  std::ifstream fs;
  fs.open(file_name);
  if ( !fs.good() ) return err::invalid_argument;
  std::stringstream buffer;
  buffer << fs.rdbuf();
  config_str = buffer.str();
  return err::success;
}

void _on_error(const reinforcement_learning::api_status& status, rl_sim* psim) {
  psim->on_error(status);
}

reinforcement_learning::live_model* rl_sim::create_live_model(const std::string& config_file, reinforcement_learning::api_status* status) {
	u::configuration config;

	if (config_file.empty()) {
		return nullptr;
	}
	// Load configuration from json config file
	if (load_config_from_json(config_file, config, status) != err::success) {
		std::cout << status->get_error_msg() << std::endl;
		return nullptr;
	}

	if (_options["log_to_file"].as<bool>()) {
		config.set(r::name::INTERACTION_SENDER_IMPLEMENTATION, r::value::INTERACTION_FILE_SENDER);
		config.set(r::name::OBSERVATION_SENDER_IMPLEMENTATION, r::value::OBSERVATION_FILE_SENDER);
	}

	if (!_options["get_model"].as<bool>()) {
		// Set the time provider to the clock time provider
		config.set(r::name::MODEL_SRC, r::value::NO_MODEL_DATA);
	}

	if (_options["log_timestamp"].as<bool>()) {
		// Set the time provider to the clock time provider
		config.set(r::name::TIME_PROVIDER_IMPLEMENTATION, r::value::CLOCK_TIME_PROVIDER);
	}

	// Trace log API calls to the console
	config.set(r::name::TRACE_LOG_IMPLEMENTATION, r::value::CONSOLE_TRACE_LOGGER);

	std::cout << " API Config " << config << std::endl;

	// Initialize the API
	return new r::live_model(config, _on_error, this);
}

int rl_sim::init_rl() {
  r::api_status status;

  // Initialize the API
  _rl_cb = std::unique_ptr<r::live_model>(create_live_model(_options["cb_json_config"].as<std::string>(), &status));
  if (_rl_cb != nullptr && _rl_cb->init(&status) != err::success ) {
    std::cout << status.get_error_msg() << std::endl;
    return -1;
  }

  _rl_ccb = std::unique_ptr<r::live_model>(create_live_model(_options["ccb_json_config"].as<std::string>(), &status));
  if (_rl_ccb != nullptr && _rl_ccb->init(&status) != err::success) {
	  std::cout << status.get_error_msg() << std::endl;
	  return -1;
  }
  
  return err::success;
}

bool rl_sim::init_sim_world() {

  //  Initilize topics
  _topics = {
    "SkiConditions-VT",
    "HerbGarden",
    "BeyBlades",
    "NYCLiving",
    "MachineLearning"
  };

  // Initialize click probability for p1
  person::topic_prob tp = {
    { _topics[0],0.08f },
    { _topics[1],0.03f },
    { _topics[2],0.05f },
    { _topics[3],0.03f },
    { _topics[4],0.25f }
  };
  _people.emplace_back("rnc", "engineering", "hiking", "spock", tp);

  // Initialize click probability for p2
  tp = {
    { _topics[0],0.08f },
    { _topics[1],0.30f },
    { _topics[2],0.02f },
    { _topics[3],0.02f },
    { _topics[4],0.10f }
  };
  _people.emplace_back("mk", "psychology", "kids", "7of9", tp);

  return true;
}

bool rl_sim::init() {
  if ( init_rl() != err::success ) return false;
  if ( !init_sim_world() ) return false;
  return true;
}

std::string rl_sim::get_action_features(const std::vector<bool>& included, std::vector<size_t>& original_ids) {
  std::ostringstream oss;
  const auto topics_count = std::count(included.begin(), included.end(), true);
  size_t counter = 0;
  // example
  // R"("_multi": [ { "TAction":{"topic":"HerbGarden"} }, { "TAction":{"topic":"MachineLearning"} } ])";
  oss << R"("_multi": [ )";
  for ( auto idx = 0; idx < _topics.size(); ++idx) {
	  if (included[idx]) {
		  original_ids[counter] = idx;
		  if (counter + 1 < topics_count)
			oss << R"({ "TAction":{"topic":")" << _topics[idx] << R"("} }, )";
		  else
			oss << R"({ "TAction":{"topic":")" << _topics.back() << R"("} } ])";
		  ++counter;
	  }
  }
  return oss.str();
}


std::string rl_sim::get_slot_features(const std::vector<std::string>& ids) {
  std::ostringstream oss;
  // example
  // R"("_slots": [ { "_id":"abc"}, {"_id":"def"} ])";
  oss << R"("_slots": [ )";
   for ( auto idx = 0; idx < ids.size() - 1; ++idx) {
    oss << R"({ "_id":")" << ids[idx] << R"("}, )";
  }
  oss << R"({ "_id":")" << ids.back() << R"("}] )";
  return oss.str();
}

void rl_sim::on_error(const reinforcement_learning::api_status& status) {
  std::cout << "Background error in Inference API: " << status.get_error_msg() << std::endl;
  std::cout << "Exiting simulation loop." << std::endl;
  _run_loop = false;
}

std::string rl_sim::create_context_json(const std::string& cntxt, const std::string& action) {
  std::ostringstream oss;
  oss << "{ " << cntxt << ", " << action << " }";
  return oss.str();
}

std::string rl_sim::create_context_json(const std::string& cntxt, const std::string& action, const std::string& slots ) {
  std::ostringstream oss;
  oss << "{ " << cntxt << ", " << action << ", " << slots << " }";
  return oss.str();
}

std::string rl_sim::create_event_id() {
  return boost::uuids::to_string(boost::uuids::random_generator()());
}

rl_sim::rl_sim(boost::program_options::variables_map vm) : _options(std::move(vm)) {}

std::string get_dist_str(const reinforcement_learning::ranking_response& response) {
  std::string ret;
  ret += "(";
  for (const auto& ap_pair : response) {
    ret += "[" + to_string(ap_pair.action_id) + ",";
    ret += to_string(ap_pair.probability) + "]";
    ret += " ,";
  }
  ret += ")";
  return ret;
}

std::string get_dist_str(const reinforcement_learning::decision_response& response) {
  std::string ret;
  ret += "(";
  for (const auto& resp : response) {
    ret += get_dist_str(resp);
    ret += " ,";
  }
  ret += ")";
  return ret;
}
