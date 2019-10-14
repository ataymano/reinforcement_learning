#pragma once
#include "logger/event_logger.h"
#include "utility/periodic_background_proc.h"

#include "factory_resolver.h"
#include "utility/watchdog.h"

#include <atomic>
#include <memory>

namespace reinforcement_learning
{
  class ranking_response;
  class api_status;

  namespace cb {
    class logger_impl {
    public:
      using error_fn = void(*)(const api_status&, void* user_context);

      int init(api_status* status);

      int report_decision(const char* event_id, const char* context, unsigned int flags, const ranking_response& response, api_status* status);

      int report_action_taken(const char* event_id, api_status* status);

      int report_outcome(const char* event_id, const char* outcome_data, api_status* status);
      int report_outcome(const char* event_id, float reward, api_status* status);

      explicit logger_impl(
        const utility::configuration& config,
        error_fn fn,
        void* err_context,
        i_trace* trace_logger,
        sender_factory_t* sender_factory,
        time_provider_factory_t* time_provider_factory);

      logger_impl(const logger_impl&) = delete;
      logger_impl(logger_impl&&) = delete;
      logger_impl& operator=(const logger_impl&) = delete;
      logger_impl& operator=(logger_impl&&) = delete;

    private:
      // Internal implementation methods
      int init_loggers(api_status* status);
      int init_trace(api_status* status);
      template<typename D>
      int report_outcome_internal(const char* event_id, D outcome, api_status* status);

    private:
      // Internal implementation state
      utility::configuration _configuration;
      error_callback_fn _error_cb;
      utility::watchdog _watchdog;

      sender_factory_t* _sender_factory;
      time_provider_factory_t* _time_provider_factory;

      std::unique_ptr<logger::interaction_logger> _ranking_logger{ nullptr };
      std::unique_ptr<logger::observation_logger> _outcome_logger{ nullptr };
      std::shared_ptr<i_trace> _trace_logger{ nullptr };
    };

    template <typename D>
    int logger_impl::report_outcome_internal(const char* event_id, D outcome, api_status* status) {
      // Clear previous errors if any
      api_status::try_clear(status);

      // Send the outcome event to the backend
      RETURN_IF_FAIL(_outcome_logger->log(event_id, outcome, status));

      // Check watchdog for any background errors. Do this at the end of function so that the work is still done.
      if (_watchdog.has_background_error_been_reported()) {
        RETURN_ERROR_LS(_trace_logger.get(), status, unhandled_background_error_occurred);
      }

      return error_code::success;
    }
  }
}
