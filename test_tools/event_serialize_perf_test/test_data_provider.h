#pragma once
#include "ranking_event.h"

#include <fstream>
#include <string>
#include <vector>

class test_data_provider {
public:
  test_data_provider(size_t features, size_t actions);

  std::string create_event_id(size_t example_id) const;

  reinforcement_learning::ranking_event& get_event( size_t example_id);

private:
  std::string create_action_features(size_t actions, size_t features, size_t example_id) const;
  std::string create_features(size_t features, size_t example_id) const;
  std::string create_context_json(const std::string& cntxt, const std::string& action) const;
  reinforcement_learning::ranking_response create_ranking_response(size_t example_id, size_t actions) const;

private:
  static const size_t preallocated_count = 100;

private:
  std::vector<reinforcement_learning::ranking_event> events;
};
#pragma once
