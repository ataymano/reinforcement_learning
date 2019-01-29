#include "test_data_provider.h"

#include "action_flags.h"
#include "data_buffer.h"
#include "ranking_event.h"

#include <sstream>
#include "serialization/json_serializer.h"

test_data_provider::test_data_provider(size_t features, size_t actions)
  : events(preallocated_count)
{
  for (size_t i = 0; i < preallocated_count; ++i) {
    const auto event_id = create_event_id(i);
    const auto context = create_context_json(create_features(features, i), create_action_features(actions, features, i));
    events[i] = reinforcement_learning::ranking_event::choose_rank(event_id.c_str(), context.c_str(), reinforcement_learning::action_flags::DEFERRED, create_ranking_response(i, actions), 0.5);
  }
}

std::string test_data_provider::create_event_id(size_t example_id) const {
  std::ostringstream oss;
  oss << "e-" << example_id;
  return oss.str();
}

std::string test_data_provider::create_action_features(size_t actions, size_t features, size_t example_id) const {
  std::ostringstream oss;
  oss << R"("_multi": [ )";
  for (size_t a = 0; a < actions; ++a) {
    oss << R"({ "TAction":{)";
    for (size_t f = 0; f < features; ++f) {
      oss << R"("a_f_)" << f << R"(":"value_)" << (a + f + example_id) << R"(")";
      if (f + 1 < features) oss << ",";
    }
    oss << "}}";
    if (a + 1 < actions) oss << ",";
  }
  oss << R"(])";
  return oss.str();
}

std::string test_data_provider::create_features(size_t features, size_t example_id) const {
  std::ostringstream oss;
  oss << R"("GUser":{)";
  oss << R"("f_int":)" << example_id << R"(,)";
  oss << R"("f_float":)" << float(example_id) + 0.5 << R"(,)";
  for (size_t f = 0; f < features; ++f) {
    oss << R"("f_str_)" << f << R"(":"value_)" << (f + example_id) << R"(")";
    if (f + 1 < features) oss << ",";
  }
  oss << R"(})";
  return oss.str();
}

reinforcement_learning::ranking_response test_data_provider::create_ranking_response(size_t example_id, size_t actions) const {
  reinforcement_learning::ranking_response result;
  for (size_t i = 0; i < actions; ++i) {
    result.push_back(i, 1. / actions);
  }
  result.set_chosen_action_id(example_id % actions);
  return result;
}

std::string test_data_provider::create_context_json(const std::string& cntxt, const std::string& action) const {
  std::ostringstream oss;
  oss << "{ " << cntxt << ", " << action << " }";
  return oss.str();
}

reinforcement_learning::ranking_event& test_data_provider::get_event(size_t example_id) {
  return events[example_id % preallocated_count];
}
