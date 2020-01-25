#include "action_flags.h"
#include "rl_logger.h"
#include "rl_logger_impl.h"
#include "err_constants.h"

#include <boost/uuid/uuid_io.hpp>
#include <boost/uuid/random_generator.hpp>

#define INIT_CHECK() do {                                       \
  if(!_initialized) {                                           \
    api_status::try_update(status, error_code::not_initialized, \
                "Library not initialized. Call init() first."); \
    return error_code::not_initialized;                         \
  }                                                             \
} while(0);                                                     \

namespace reinforcement_learning
{
  rl_logger::rl_logger(
    const utility::configuration& config,
    error_fn fn,
    void* err_context,
    trace_logger_factory_t* trace_factory,
    sender_factory_t* s_factory,
    time_provider_factory_t* time_prov_factory)
  {
    _pimpl = std::unique_ptr<rl_logger_impl>(
    new rl_logger_impl(config, fn, err_context, trace_factory, s_factory, time_prov_factory));
  }

  rl_logger::rl_logger(rl_logger&& other) {
    std::swap(_pimpl, other._pimpl);
    _initialized = other._initialized;
  }

  rl_logger::~rl_logger() = default;

  rl_logger& rl_logger::operator=(rl_logger&& other) {
    std::swap(_pimpl, other._pimpl);
    _initialized = other._initialized;
    return *this;
  }

  int rl_logger::init(api_status* status) {
    if (_initialized)
      return error_code::success;

    const auto err_code = _pimpl->init(status);
    if (err_code == error_code::success) {
      _initialized = true;
    }

    return err_code;
  }

  int rl_logger::log(const char * event_id, const char * context_json, const ranking_response& resp, float outcome, api_status* status)
  {
    INIT_CHECK();
    RETURN_IF_FAIL(_pimpl->report_decision(event_id, context_json, action_flags::DEFAULT, resp, status));
    return _pimpl->report_outcome(event_id, outcome, status);
  }

  int rl_logger::log(const char * event_id, const char * context_json, const ranking_response& resp, const char* outcome, api_status* status)
  {
    INIT_CHECK();
    RETURN_IF_FAIL(_pimpl->report_decision(event_id, context_json, action_flags::DEFAULT, resp, status));
    return _pimpl->report_outcome(event_id, outcome, status);
  }

  int rl_logger::log(const char * context_json, const ranking_response& resp, float outcome, api_status* status)
  {
    INIT_CHECK();
    const auto event_id = boost::uuids::to_string(boost::uuids::random_generator()());
    RETURN_IF_FAIL(_pimpl->report_decision(event_id.c_str(), context_json, action_flags::DEFAULT, resp, status));
    return _pimpl->report_outcome(event_id.c_str(), outcome, status);
  }

  int rl_logger::log(const char * context_json, const ranking_response& resp, const char* outcome, api_status* status)
  {
    INIT_CHECK();
    const auto event_id = boost::uuids::to_string(boost::uuids::random_generator()());
    RETURN_IF_FAIL(_pimpl->report_decision(event_id.c_str(), context_json, action_flags::DEFAULT, resp, status));
    return _pimpl->report_outcome(event_id.c_str(), outcome, status);
  }
}
