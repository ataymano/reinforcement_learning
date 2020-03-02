#include "config_utility.h"
#include "constants.h"
#include "live_model.h"
#include "ranking_response.h"
#include "onnx_extension.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <thread>

// Namespace manipulation for brevity
namespace r = reinforcement_learning;
namespace u = r::utility;
namespace cfg = u::config;
namespace err = r::error_code;
using namespace std;

void require_success(const r::api_status& status)
{
    if (status.get_error_code() != r::error_code::success) {
        throw runtime_error(status.get_error_msg());
    }
}

void logging_error_fn(const r::api_status& status, void*)
{
  std::cerr << status.get_error_msg() << std::endl;
}


struct example {
    const size_t label;
    const string context;

    example(size_t _label, const string& _context)
    : label(_label)
    , context(_context)
    {}
};

vector<example> LoadMnist(const string& path) {
    ifstream tensors(path);
    string labeled_tensor;
    vector<example> result;
    while (tensors >> labeled_tensor) {
        const auto sep = labeled_tensor.find_first_of("|");
        size_t label = stoi(labeled_tensor.substr(0, sep));
        const string context = R"({"input.1":)" + labeled_tensor.substr(sep + 1) + "}";
        result.emplace_back(label, context);
    }
    return result;
}

//! Load contents of file into a string
int load_file(const std::string& file_name, std::string& config_str) {
  std::ifstream fs;
  fs.open(file_name);
  if ( !fs.good() )
    return reinforcement_learning::error_code::invalid_argument;
  std::stringstream buffer;
  buffer << fs.rdbuf();
  config_str = buffer.str();
  return reinforcement_learning::error_code::success;
}

//! Load config from json file
int load_config_from_json(const std::string& file_name, u::configuration& config) {
  std::string config_str;
  const auto scode = load_file(file_name, config_str);
  if ( scode != 0 ) return scode;
  return cfg::create_from_json(config_str, config);
}

r::live_model create_live_model(const string& config_path) {
    r::api_status status;
    u::configuration config;
    if( load_config_from_json(config_path, config) != err::success ) {
        throw  runtime_error("Unable to Load file: " + config_path);
    }
    r::live_model model(config, logging_error_fn, nullptr, &r::trace_logger_factory, &r::data_transport_factory, &r::model_factory, &r::sender_factory);
    require_success(status);
    model.init(&status);
    require_success(status);
    return model;
}


int main(int argc, char** argv) {
    const string tensors_path = "/mnist/mnist_test_data.txt";
    const string config_path(argv[1]);
    r::onnx::register_onnx_factory();
    const auto examples = LoadMnist(tensors_path);
    auto model = create_live_model(config_path);
    this_thread::sleep_for(std::chrono::milliseconds(10000));
    int i = 0;
    r::api_status status;

    while (true) {
        const string id = "Event" + to_string(i++);
        const auto index = rand() % examples.size();
        const auto& example = examples[index];
        r::ranking_response response;
        cout << id << ": ";
        model.choose_rank(id.c_str(), example.context.c_str(), response, &status);
        require_success(status);
        cout << " ranked, ";
        size_t chosen_action_id;
        response.get_chosen_action_id(chosen_action_id, &status);
        require_success(status);

        if (chosen_action_id == example.label) {
            model.report_outcome(id.c_str(), 1, &status);
            require_success(status);
            cout << "rewarded" << endl;
        }
        else {
            cout << "non rewarded" << endl;
        }

        this_thread::sleep_for(std::chrono::milliseconds(2000));
    }
    std::cout << "Hi!" << std::endl;
}