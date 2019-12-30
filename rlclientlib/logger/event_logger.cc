#include "event_logger.h"
#include "ranking_event.h"
#include "err_constants.h"
#include "time_helper.h"
namespace reinforcement_learning { namespace logger {

  int interaction_logger::log(const char* event_id, const char* context, unsigned int flags, const ranking_response& response, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(ranking_event::choose_rank(event_id, context, flags, response, now), status);
  }

  int ccb_logger::log_decisions(std::vector<const char*>& event_ids, const char* context, unsigned int flags, const std::vector<std::vector<uint32_t>>& action_ids,
    const std::vector<std::vector<float>>& pdfs, const std::string& model_version, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(std::move(decision_ranking_event::request_decision(event_ids, context, flags, action_ids, pdfs, model_version, now)), status);
  }

  int observation_logger::report_action_taken(const char* event_id, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(outcome_event::report_action_taken(event_id, now), status);
  }

  int generic_logger::log_interaction(const char* episode_id, const char* event_id, const char* payload, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(generic_event::interaction(episode_id, event_id, payload, now), status);
  }

  int generic_logger::log_observation(const char* episode_id, const char* event_id, const char* payload, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(generic_event::observation(episode_id, event_id, payload, now), status);
  }

  int generic_logger::close_session(const char* episode_id, api_status* status) {
    const auto now = _time_provider != nullptr ? _time_provider->gmt_now() : timestamp();
    return append(generic_event::close_session(episode_id,  now), status);
  }

}}
