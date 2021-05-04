#include "multistep_example_joiner.h"

#include "generated/v2/DedupInfo_generated.h"
#include "generated/v2/Event_generated.h"
#include "generated/v2/Metadata_generated.h"
#include "generated/v2/OutcomeEvent_generated.h"
#include "io/logger.h"

#include <limits.h>
#include <time.h>

// VW headers
#include "example.h"
#include "io/logger.h"
#include "parse_example_json.h"
#include "parser.h"
#include "v_array.h"


multistep_example_joiner::multistep_example_joiner(vw *vw)
    : _vw(vw), _reward_calculation(&RewardFunctions::earliest) {}

multistep_example_joiner::~multistep_example_joiner() {
  // cleanup examples
  for (auto *ex : _example_pool) {
    VW::dealloc_examples(ex, 1);
  }
}

int multistep_example_joiner::process_event(const v2::JoinedEvent &joined_event) {
  return 0;
}

void multistep_example_joiner::set_default_reward(float default_reward) {
  _default_reward = default_reward;
}

void multistep_example_joiner::set_learning_mode_config(const v2::LearningModeType& learning_mode) {
  _learning_mode_config = learning_mode;
}

void multistep_example_joiner::set_problem_type_config(const v2::ProblemType& problem_type) {
  _problem_type_config = problem_type;
}

void multistep_example_joiner::set_reward_function(const v2::RewardFunctionType type) {
  using namespace RewardFunctions;

  switch (type) {
  case v2::RewardFunctionType_Earliest:
    _reward_calculation = &earliest;
    break;
  case v2::RewardFunctionType_Average:
    _reward_calculation = &average;
    break;

  case v2::RewardFunctionType_Sum:
    _reward_calculation = &sum;
    break;

  case v2::RewardFunctionType_Min:
    _reward_calculation = &min;
    break;

  case v2::RewardFunctionType_Max:
    _reward_calculation = &max;
    break;

  case v2::RewardFunctionType_Median:
    _reward_calculation = &median;
    break;

  default:
    break;
  }
}

int multistep_example_joiner::process_joined(v_array<example *> &examples) {
  return 0;
}

bool multistep_example_joiner::processing_batch() {
    return false;
}
