#pragma once

#include <vector>

#include "ranking_event.h"
#include "utility/data_buffer.h"

namespace reinforcement_learning {

  template<typename T>
  struct json_event_serializer;

  template <>
  struct json_event_serializer<ranking_event> {
    using buffer_t = utility::data_buffer;

    static void serialize(ranking_event& evt, buffer_t& buffer) {
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
    }
  };

  template<>
  struct json_event_serializer<outcome_event> {
    using buffer_t = utility::data_buffer;

    static void serialize(outcome_event& evt, buffer_t& buffer)
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
      default:
        throw "Real exception";
      }
    }
  };

  template <typename event_t>
  struct json_collection_serializer {
    using serializer_t = json_event_serializer<event_t>;
    using buffer_t = utility::data_buffer;

    json_collection_serializer(buffer_t& buffer) :
      _buffer(buffer)
    {}

    void add(event_t& evt) {
      serializer_t::serialize(evt, _buffer);
      _buffer << "\n";
    }

    uint64_t size() const {
      return _buffer.size();
    }

    void reset() {
      _buffer.reset();
    }

    void finalize() {
      _buffer.remove_last();
    }

    buffer_t& _buffer;
  };
}
