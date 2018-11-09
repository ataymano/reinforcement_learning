#pragma once

#include <vector>

#include <flatbuffers/flatbuffers.h>

#include "logger/flatbuffer_allocator.h"
#include "generated/OutcomeEvent_generated.h"
#include "generated/RankingEvent_generated.h"

#include <iostream>

namespace reinforcement_learning {

  template<typename T>
  struct fb_event_serializer;

  template<>
  struct fb_event_serializer<ranking_event> {
    using fb_event_t = RankingEvent;
    using offset_vector_t = typename std::vector<flatbuffers::Offset<fb_event_t>>;
    using batch_buider_t = messages::RankingEventBatchBuilder;

    static flatbuffers::Offset<fb_event_t> serialize(ranking_event& evt, flatbuffers::FlatBufferBuilder& builder) {
      const auto event_id_offset = builder.CreateString(evt.get_event_id());
      const auto action_ids_vector_offset = builder.CreateVector(evt.get_action_ids());
      const auto probabilities_vector_offset = builder.CreateVector(evt.get_probabilities());
      const auto context_offset = builder.CreateVector(evt.get_context());
      const auto model_id_offset = builder.CreateString(evt.get_model_id());
      return messages::CreateRankingEvent(builder,
        event_id_offset,
        evt.get_defered_action(),
        action_ids_vector_offset,
        context_offset,
        probabilities_vector_offset,
        model_id_offset);
    }
  };

  template<>
  struct fb_event_serializer<outcome_event> {
    using fb_event_t = OutcomeEvent;
    using offset_vector_t = std::vector<flatbuffers::Offset<fb_event_t>>;
    using batch_buider_t = messages::OutcomeEventBatchBuilder;

    static flatbuffers::Offset<fb_event_t> serialize(outcome_event& evt, flatbuffers::FlatBufferBuilder& builder)
    {
      auto event_id_offset = builder.CreateString(evt.get_event_id());

      flatbuffers::Offset<void> any_event;
      messages::OutcomeEventAny type = messages::OutcomeEventAny_NONE;
      switch(evt.get_outcome_type())
      {
        case outcome_event::outcome_type_string:
        {
          type = messages::OutcomeEventAny_OutcomeEventString;
          auto outcome_offset = builder.CreateString(evt.get_outcome());
          any_event = messages::CreateOutcomeEventString(builder, event_id_offset, outcome_offset).Union();
          break;
        }
        case outcome_event::outcome_type_numeric:
        {
          type = messages::OutcomeEventAny_OutcomeEventNumeric;
          any_event = messages::CreateOutcomeEventNumeric(builder, event_id_offset, evt.get_numeric_outcome()).Union();
          break;
        }
        case outcome_event::outcome_type_action_taken:
        {
          type = messages::OutcomeEventAny_OutcomeEventTaken;
          any_event = messages::CreateOutcomeEventTaken(builder, event_id_offset).Union();
          break;
        }
        default:
          throw "Real exception";
        break;
      }
      return messages::CreateOutcomeEvent(builder, type, any_event);
    }
  };

  template <typename event_t>
  struct fb_collection_serializer {
    using serializer_t = fb_event_serializer<event_t>;
    using buffer_t = utility::data_buffer;

    fb_collection_serializer(buffer_t& buffer) :
      _builder(buffer.capacity(), &_allocator),
      _allocator(buffer),
      _buffer(buffer)
    {}

    void add(event_t& evt) {
      auto const offset = serializer_t::serialize(evt, _builder);
      _event_offsets.push_back(offset);
    }

    uint64_t size() const {
      return _builder.GetSize();
    }

    void finalize() {
      auto event_offsets = _builder.CreateVector(_event_offsets);
      typename serializer_t::batch_buider_t batch_builder(_builder);
      batch_builder.add_events(event_offsets);
      auto orc = batch_builder.Finish();
      _builder.Finish(orc);

      //std::cerr << "flat buf" << _builder.GetBufferPointer() << "\n";
      //std::cerr << "buf" << _buffer.data() << "\n";
      auto offset = _builder.GetBufferPointer() - _buffer.data();
      _buffer.set_begin_offset(offset);
      //std::cerr << "offset" << offset << "\n";
      //std::cerr << "new buff" << _buffer.data() << "\n";
    }

    void reset() {
      _builder.Clear();
      _buffer.reset();
    }

    typename serializer_t::offset_vector_t _event_offsets;
    flatbuffers::FlatBufferBuilder _builder;
    flatbuffer_allocator _allocator;
    buffer_t& _buffer;
  };
}
