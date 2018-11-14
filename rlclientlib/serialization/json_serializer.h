#pragma once

#include <vector>

#include "ranking_event.h"
#include "utility/data_buffer.h"
#include "logger/message_type.h"
#include "api_status.h"

namespace reinforcement_learning { namespace logger {

  template<typename T>
  struct json_event_serializer;

  template <>
  struct json_event_serializer<ranking_event> {
    using buffer_t = utility::data_buffer;

    static int serialize(ranking_event& evt, buffer_t& buffer, api_status* status) {
      // Add version and eventId
      buffer << R"({"Version":"1","EventId":")" << evt.get_event_id() << R"(")";
      if (evt.get_defered_action()) {
        buffer << R"(,"DeferredAction":true)";
      }

      // Add action ids
      buffer << R"(,"a":[)";
      auto delimiter = "";
      for (auto const& action_id : evt.get_action_ids()) {
        buffer << delimiter << action_id + 1;
        delimiter = ",";
      }

      // Add context
      char* context = reinterpret_cast<char*>(&(evt.get_context()[0]));
      //std::string context(evt.get_context().begin(), evt.get_context().end())
      buffer << R"(],"c":)" << context << R"(,"p":[)";

      // Add probabilities
      delimiter = "";
      for (auto const& probability : evt.get_probabilities()) {
        buffer << delimiter << probability + 1;
        delimiter = ",";
      }

      //add model id
      buffer << R"(],"VWState":{"m":")" << evt.get_model_id() << R"("})";



      if (evt.get_pass_prob() < 1) {
        buffer << R"(,"pdrop":)" << (1 - evt.get_pass_prob());
      }
      buffer << R"(})";

      return error_code::success;
    }
  };

  template<>
  struct json_event_serializer<outcome_event> {
    using buffer_t = utility::data_buffer;

    static int serialize(outcome_event& evt, buffer_t& buffer, api_status* status)
    {
      switch (evt.get_outcome_type())
      {
        case outcome_event::outcome_type_string:
          buffer << R"({"EventId":")" << evt.get_event_id() << R"(","v":)" << evt.get_outcome() << R"(})";
          break;
        case outcome_event::outcome_type_numeric:
          buffer << R"({"EventId":")" << evt.get_event_id() << R"(","v":)" << evt.get_numeric_outcome() << R"(})";
          break;
        case outcome_event::outcome_type_action_taken:
          buffer << R"({"EventId":")" << evt.get_event_id() << R"(","ActionTaken":true})";
          break;
        default: {
          return report_error(status, error_code::serialize_unknown_outcome_type, error_code::serialize_unknown_outcome_type_s);
        }
      }
      return error_code::success;
    }
  };

  template <typename event_t>
  struct json_collection_serializer {
    using serializer_t = json_event_serializer<event_t>;
    using buffer_t = utility::data_buffer;

    static int message_id() { return 0; }

    json_collection_serializer(buffer_t& buffer) :
      _buffer(buffer)
    {}

    int add(event_t& evt, api_status* status) {
      RETURN_IF_FAIL(serializer_t::serialize(evt, _buffer, status));
      _buffer << "\n";
      return error_code::success;
    }

    uint64_t size() const {
      return _buffer.body_size();
    }

    void reset() {
      _buffer.reset();
    }

    void finalize() {
      _buffer.remove_last();
    }

    buffer_t& _buffer;
  };

  template<>
  inline int json_collection_serializer<outcome_event>::message_id() { return message_type::json_outcome_event_collection; }

  template<>
  inline int json_collection_serializer<ranking_event>::message_id() { return message_type::json_ranking_event_collection; }
}}
