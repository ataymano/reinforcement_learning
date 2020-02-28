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
        throw new runtime_error(status.get_error_msg());
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
        const string context = R"({"Input3":)" + labeled_tensor.substr(sep + 1) + "}";
        result.emplace_back(label, context);
    }
    return result;
}

r::live_model create_pretrained_model(const std::string& model_path) {
    const char* JSON_CFG = R"(
    {
        "appid": "onnxtest",
        "model.implementation": "ONNXRUNTIME",
        "onnx.parse_feature_string": true,
        "onnx.output_name": "17",
        "IsExplorationEnabled": true,
        "model.source": "FILE_MODEL_DATA",
        "model_file_loader.file_must_exist": true,
        "EventHubInteractionConnectionString": "Endpoint=sb://localhost:8080/;SharedAccessKeyName=RMSAKey;SharedAccessKey=<ASharedAccessKey>=;EntityPath=interaction",
        "EventHubObservationConnectionString": "Endpoint=sb://localhost:8080/;SharedAccessKeyName=RMSAKey;SharedAccessKey=<ASharedAccessKey>=;EntityPath=observation",
        "InitialExplorationEpsilon": 1.0,
        "model.backgroundrefresh": false
    }
    )";

    r::api_status status;
    u::configuration config;
    u::config::create_from_json(JSON_CFG, config, nullptr, &status);
    require_success(status);
    // TODO: This should be a CMake-configure set value
    config.set("model_file_loader.file_name", model_path.c_str());
    
    r::live_model model(config, logging_error_fn, nullptr, &r::trace_logger_factory, &r::data_transport_factory, &r::model_factory, &r::sender_factory);
    require_success(status);
    model.init(&status);
    require_success(status);
    return model;
}


r::live_model create_live_eh_model() {
    const char* JSON_CFG = R"(
    {
        "appid": "onnxtest",
        "model.implementation": "ONNXRUNTIME",
        "onnx.parse_feature_string": true,
        "onnx.output_name": "Plus214_Output_0",
        "IsExplorationEnabled": true,
        "EventHubInteractionConnectionString": "Endpoint=sb://ingestft6zgq5xpytri.servicebus.windows.net/;SharedAccessKeyName=FrontEndAccessKey;SharedAccessKey=h6s7X7UJ4XQIccv333qLzCispRXAGL3bUnvy7rxptHs=;EntityPath=interaction",
        "EventHubObservationConnectionString": "Endpoint=sb://ingestft6zgq5xpytri.servicebus.windows.net/;SharedAccessKeyName=FrontEndAccessKey;SharedAccessKey=h6s7X7UJ4XQIccv333qLzCispRXAGL3bUnvy7rxptHs=;EntityPath=observation",
        "InitialExplorationEpsilon": 1.0,
        "model.backgroundrefresh": false
    }
    )";
    r::api_status status;
    u::configuration config;
    u::config::create_from_json(JSON_CFG, config, nullptr, &status);
    require_success(status);
    // TODO: This should be a CMake-configure set value
    config.set(r::name::MODEL_BLOB_URI, "https://ataymanodev.blob.core.windows.net/byom/current?st=2020-02-28T18%3A01%3A46Z&se=2022-02-28T18%3A01%3A00Z&sp=rl&sv=2018-03-28&sr=b&sig=tElAn9d66oJCnRyQNjAXgLItAKiiPznDzRYumT0s1F0%3D");
    
    r::live_model model(config, logging_error_fn, nullptr, &r::trace_logger_factory, &r::data_transport_factory, &r::model_factory, &r::sender_factory);
    require_success(status);
    model.init(&status);
    require_success(status);
    return model;
}


int main() {
    const string tensors_path = "/mnist/mnist_test_data.txt";
    const string configs_path = "";
    r::onnx::register_onnx_factory();
    const auto examples = LoadMnist(tensors_path);
    auto model = create_pretrained_model("/mnist/current.onnx");
 //   auto model = create_pretrained_model("/mnist/mnist_model.onnx");
 //   auto model = create_live_eh_model();
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