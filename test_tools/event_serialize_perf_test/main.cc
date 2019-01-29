#include "test_data_provider.h"

#include "api_status.h"
#include "serialization/fb_serializer.h"
#include "data_buffer.h"
#include <boost/program_options.hpp>

#include <iostream>
#include <thread>

namespace po = boost::program_options;



bool is_help(const po::variables_map& vm) {
  return vm.count("help") > 0;
}

po::variables_map process_cmd_line(const int argc, char** argv) {
  po::options_description desc("Options");
  desc.add_options()
    ("help", "produce help message")
    ("batches,b", po::value<size_t>()->default_value(10), "Number of batches")
    ("examples,n", po::value<size_t>()->default_value(10), "Number of examples per batch")
    ("features,x", po::value<size_t>()->default_value(10), "Features count")
    ("actions,a", po::value<size_t>()->default_value(2), "Number of actions")
    ;

  po::variables_map vm;
  store(parse_command_line(argc, argv, desc), vm);

  if (is_help(vm))
    std::cout << desc << std::endl;

  return vm;
}

template<class Serializer>
void Test(test_data_provider& tdp, size_t examples, size_t batches) {
  reinforcement_learning::utility::data_buffer db;
  Serializer fcs(db);
  for (size_t j = 0; j < examples; ++j) {
    auto& evt = tdp.get_event(j);
    fcs.add(evt);
  }
  fcs.finalize();
  std::cout << "Buffer size: " << db.body_filled_size() << std::endl;

  const auto start = std::chrono::high_resolution_clock::now();
  for (size_t i = 0; i < batches; ++i) {
    reinforcement_learning::utility::data_buffer db;
    Serializer fcs(db);
    for (size_t j = 0; j < examples; ++j) {
      auto& evt = tdp.get_event(i * examples + j);
      fcs.add(evt);
    }
    fcs.finalize();
  }
  const auto end = std::chrono::high_resolution_clock::now();
  const auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
  std::cout << "Total: " << duration << std::endl;
  std::cout << "Normalized: " << duration / (batches * examples) << std::endl;

}

int main(int argc, char** argv) {
  try {
    const auto vm = process_cmd_line(argc, argv);
    if (is_help(vm)) return 0;

    const auto batches = vm["batches"].as<size_t>();
    const auto examples = vm["examples"].as<size_t>();
    const auto features = vm["features"].as<size_t>();
    const auto actions = vm["actions"].as<size_t>();

    test_data_provider tdp(features, actions);

    const auto& first = tdp.get_event(0);
    std::cout << "test data: " << std::endl;
    std::cout << "    context size: " << first.get_context().size() << std::endl << std::endl;
    
    std::cout << "Old: " <<  std::endl;
    Test<reinforcement_learning::logger::fb_collection_serializer<reinforcement_learning::ranking_event>>(tdp, examples, batches);
    std::cout << std::endl << "New: " << std::endl;
    Test<reinforcement_learning::logger::fb_collection_serializer2<reinforcement_learning::ranking_event>>(tdp, examples, batches);
    return 0;
  }
  catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl;
    return -1;
  }
}
