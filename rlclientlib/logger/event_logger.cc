#include "event_logger.h"
#include "ranking_event.h"
#include "err_constants.h"
#include "time_helper.h"
namespace reinforcement_learning { namespace logger {

  int interaction_logger::log(const char* context, unsigned int flags, learning_mode learning_mode, const ranking_response& response, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(ranking_event::choose_rank(context, flags, response, now, learning_mode), status);
  }

  int ccb_logger::log(const char* context, unsigned int flags, const decision_response& response, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(std::move(decision_ranking_event::request_decision(context, flags, response, now)), status);
  }

  int observation_logger::report_action_taken(const char* event_id, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(outcome_event::report_action_taken(event_id, now), status);
}
}}
