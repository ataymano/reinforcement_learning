#pragma once
#include "model_mgmt.h"
#include "ranking_response.h"
#include "decision_response.h"

#include <vector>

namespace reinforcement_learning {
  class i_trace;
}

namespace reinforcement_learning {
  int populate_response(size_t chosen_action_index, std::vector<int>& action_ids, std::vector<float>& pdf, std::string&& model_id, ranking_response& response, i_trace* trace_logger, api_status* status);
  int populate_response(const std::vector<std::vector<uint32_t>>& action_ids, const std::vector<std::vector<float>>& pdfs, const std::vector<const char*>& event_ids, std::string&& model_id, decision_response& response, i_trace* trace_logger, api_status* status);
  int sample_and_populate_response(uint64_t rnd_seed, std::vector<int>& action_ids, std::vector<float>& pdf, std::string&& model_id, ranking_response& response, i_trace* trace_logger, api_status* status);
}
