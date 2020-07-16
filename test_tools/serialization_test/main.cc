#include "action_flags.h"
#include "api_status.h"
#include "ranking_event.h"
#include "time_helper.h"
#include "data_buffer.h"
#include "serialization/fb_serializer.h"
#include <flatbuffers/flatbuffers.h>
#include "logger/flatbuffer_allocator.h"

#include "generated/MemoryTestEventNew_generated.h"
#include "generated/RankingEvent_generated.h"
#include "generated/OutcomeEvent_generated.h"

#include "generated/EnvelopeTestEventUnion_generated.h"
#include "generated/EnvelopeTestEventBytes_generated.h"

#include <boost/program_options.hpp>

#include <thread>

#include <iostream>

namespace po = boost::program_options;
namespace rl = reinforcement_learning;
namespace u=rl::utility;

using payload_t = std::vector<unsigned char>;

std::string generate_string(size_t kb) {
  const size_t size = kb * 1024;
  std::vector<char> buffer(size, '1');
  return std::string(&buffer[0], size);
}

std::vector<unsigned char> generate_byte_array(size_t kb) {
  const size_t size = kb * 1024;
  return std::vector<unsigned char>(size, '1');
}

payload_t GetMemoryTestLegacyOutcomeBuffer() {
    flatbuffers::FlatBufferBuilder fbb(1024);
    const auto event_id = fbb.CreateString("event_id");
    const auto number_event = CreateNumericEvent(fbb, 8).Union();
    TimeStamp client_ts(2020, 1, 2, 3, 4, 5, 6);
	  const auto meta_id_offset = CreateMetadata(fbb, &client_ts);
    auto retval = CreateOutcomeEventHolder(fbb, event_id, 0.5, OutcomeEvent_NumericEvent,
                                            number_event, meta_id_offset);
    fbb.Finish(retval);
    const auto result = payload_t(fbb.GetBufferPointer(), fbb.GetBufferPointer() + fbb.GetSize());
    return result;
}

payload_t GetMemoryTestLegacyCbEventBuffer(int context_size_kb) {
  flatbuffers::FlatBufferBuilder fbb(1024);
  const auto event_id = fbb.CreateString("event_id");
  TimeStamp client_ts(2020, 1, 2, 3, 4, 5, 6);
  const auto meta_offset = CreateMetadata(fbb, &client_ts);

  const auto action_offset = fbb.CreateVector(std::vector<uint64_t> {1, 2, 3, 4, 5});
  const auto probabilities_offset = fbb.CreateVector(std::vector<float> {0.2, 0.2, 0.2, 0.2, 0.2});
  const auto context_offset = fbb.CreateVector(generate_byte_array(context_size_kb));
  const auto model_id_offset = fbb.CreateString("model-id");

  auto retval = CreateRankingEvent(fbb, event_id, true, action_offset, context_offset, probabilities_offset, model_id_offset, 0.5, meta_offset);

  fbb.Finish(retval);
  const auto result = payload_t(fbb.GetBufferPointer(), fbb.GetBufferPointer() + fbb.GetSize());
  return result;
}

payload_t GetMemoryTestNewCbEventBuffer(int context_size_kb, bool withOutcome) {
  flatbuffers::FlatBufferBuilder fbb(1024);
  
  const bool withContext = context_size_kb > 0;

  if (!withContext && !withOutcome) {
    throw "Please specify either context or reward";
  }
  const auto event_id = fbb.CreateString("event_id");
  TimeStamp client_ts(2020, 1, 2, 3, 4, 5, 6);
  const auto meta_offset = CreateMetadata(fbb, &client_ts);

  flatbuffers::Offset<CbInteractionNew> interaction_offset = 0;

  if (withContext) {
    const flatbuffers::Offset<flatbuffers::Vector<uint64_t>> action_offset = fbb.CreateVector(std::vector<uint64_t> {1, 2, 3, 4, 5});
    const flatbuffers::Offset<flatbuffers::Vector<float>> probabilities_offset = fbb.CreateVector(std::vector<float> {0.2, 0.2, 0.2, 0.2, 0.2});
    const flatbuffers::Offset<flatbuffers::Vector<uint8_t>> context_offset = fbb.CreateVector(generate_byte_array(context_size_kb));
    const flatbuffers::Offset<flatbuffers::String> model_id_offset = fbb.CreateString("model-id");

    interaction_offset = CreateCbInteractionNew(fbb,
      true,
      action_offset,
      context_offset,
      probabilities_offset,
      model_id_offset
    );
  }

  const OutcomeEvent outcome_type = withOutcome ? OutcomeEvent_NumericEvent : OutcomeEvent_NONE;
  const auto number_event = withOutcome ? CreateNumericEvent(fbb, 8).Union() : 0;


  auto retval = CreateMemoryTestEventNew(fbb,
    event_id,
    0.5,
    meta_offset,
    interaction_offset,
    outcome_type,
    number_event);

  fbb.Finish(retval);
  const auto result = payload_t(fbb.GetBufferPointer(), fbb.GetBufferPointer() + fbb.GetSize());
  return result;
}

template<typename TEvent>
TEvent Generate(size_t) {
  throw "Not supported";
}

template<>
rl::ranking_event Generate(size_t size) {
  rl::ranking_response rr;
  rr.set_event_id("event_id");
  rr.set_chosen_action_id(1);
  rr.set_model_id("model");
  rr.push_back(0, 0.8);
  rr.push_back(1, 0.2);
  return rl::ranking_event::choose_rank("event_id", generate_string(size).c_str(), rl::action_flags::DEFAULT, rr, rl::timestamp{ 2020, 1, 2, 3, 4, 5, 6}, 0.5);
}

struct union_serializer {
  using buffer_t = rl::utility::data_buffer;

  union_serializer(buffer_t& buffer)
    : _allocator(buffer), _builder(buffer.body_capacity(), &_allocator), _buffer(buffer) {}

  static int serialize(rl::ranking_event& evt, flatbuffers::FlatBufferBuilder& builder,
    flatbuffers::Offset<EnvelopeUnion>& ret_val) {
    const auto& ts = evt.get_client_time_gmt();
    TimeStamp client_ts(ts.year, ts.month, ts.day, ts.hour,
      ts.minute, ts.second, ts.sub_second);
    ret_val = CreateEnvelopeUnionDirect(builder,
      evt.get_event_id().c_str(),
      evt.get_pass_prob(),
      CreateMetadata(builder, &client_ts),
      Interaction_EnvelopeTestCbInteraction,
      CreateEnvelopeTestCbInteractionDirect(
        builder,
        evt.get_defered_action(),
        &evt.get_action_ids(),
        &evt.get_context(),
        &evt.get_probabilities(),
        evt.get_model_id().c_str(), LearningModeType_Online).Union());
    return rl::error_code::success;
  }

  void add(rl::ranking_event& evt) {
    flatbuffers::Offset<EnvelopeUnion> offset;
    serialize(evt, _builder, offset);
    _event_offsets.push_back(offset);
  }

  uint64_t size() const { return _builder.GetSize(); }

  void finalize() {
    auto event_offsets = _builder.CreateVector(_event_offsets);
    EnvelopeUnionBatchBuilder batch_builder(_builder);
    batch_builder.add_events(event_offsets);
    auto batch_offset = batch_builder.Finish();
    _builder.Finish(batch_offset);
    // Where does the body of the data begin in relation to the start
    // of the raw buffer
    const auto offset = _builder.GetBufferPointer() - _buffer.raw_begin();
    _buffer.set_body_endoffset(_buffer.preamble_size() + _buffer.body_capacity());
    _buffer.set_body_beginoffset(offset);
  }

  std::vector<flatbuffers::Offset<EnvelopeUnion>> _event_offsets;
  rl::flatbuffer_allocator _allocator;
  flatbuffers::FlatBufferBuilder _builder;
  buffer_t& _buffer;
};

class bytes_payload_event : public rl::event {
public:
  bytes_payload_event(const char* event_id, const rl::timestamp& ts, float pass_prob, payload_t&& payload)
  : rl::event(event_id, ts, pass_prob)
  , _payload(std::move(payload)) {}

  bytes_payload_event(const bytes_payload_event& other) = default;
  bytes_payload_event(bytes_payload_event&& other) = default;
  bytes_payload_event& operator=(const bytes_payload_event& other) = default;
  bytes_payload_event& operator=(bytes_payload_event&& other) = default;
  ~bytes_payload_event() = default;

  const std::vector<unsigned char>& get_payload() const {
    return _payload;
  }

  const std::string& get_event_id() const { return get_seed_id(); }
private:
  std::vector<unsigned char> _payload;
};


payload_t GenerateBytesPayload(int context_size_kb) {
  flatbuffers::FlatBufferBuilder fbb(1024);

  const flatbuffers::Offset<flatbuffers::Vector<uint64_t>> action_offset = fbb.CreateVector(std::vector<uint64_t> {1, 2, 3, 4, 5});
  const flatbuffers::Offset<flatbuffers::Vector<float>> probabilities_offset = fbb.CreateVector(std::vector<float> {0.2, 0.2, 0.2, 0.2, 0.2});
  const flatbuffers::Offset<flatbuffers::Vector<uint8_t>> context_offset = fbb.CreateVector(generate_byte_array(context_size_kb));
  const flatbuffers::Offset<flatbuffers::String> model_id_offset = fbb.CreateString("model-id");

  auto retval = CreateCbInteractionNew(fbb,
    true,
    action_offset,
    context_offset,
    probabilities_offset,
    model_id_offset
  );

  fbb.Finish(retval);
  return payload_t(fbb.GetBufferPointer(), fbb.GetBufferPointer() + fbb.GetSize());
}

template<>
bytes_payload_event Generate(size_t size) {
  rl::timestamp ts{ 2020, 1, 2, 3, 4, 5, 6 };
  return bytes_payload_event("event_id", ts, 0.5, std::move(GenerateBytesPayload(size)));
}

struct bytes_serializer {
  using buffer_t = rl::utility::data_buffer;

  bytes_serializer(buffer_t& buffer)
    : _allocator(buffer), _builder(buffer.body_capacity(), &_allocator), _buffer(buffer) {}

  static int serialize(bytes_payload_event& evt, flatbuffers::FlatBufferBuilder& builder,
    flatbuffers::Offset<EnvelopeBytes>& ret_val) {
    const auto& ts = evt.get_client_time_gmt();
    TimeStamp client_ts(ts.year, ts.month, ts.day, ts.hour,
      ts.minute, ts.second, ts.sub_second);
    ret_val = CreateEnvelopeBytesDirect(builder,
      evt.get_event_id().c_str(),
      evt.get_pass_prob(),
      CreateMetadata(builder, &client_ts),
      0,
      &evt.get_payload());
    return rl::error_code::success;
  }

  void add(bytes_payload_event& evt) {
    flatbuffers::Offset<EnvelopeBytes> offset;
    serialize(evt, _builder, offset);
    _event_offsets.push_back(offset);
  }

  uint64_t size() const { return _builder.GetSize(); }

  void finalize() {
    auto event_offsets = _builder.CreateVector(_event_offsets);
    EnvelopeBytesBatchBuilder batch_builder(_builder);
    batch_builder.add_events(event_offsets);
    auto batch_offset = batch_builder.Finish();
    _builder.Finish(batch_offset);
    // Where does the body of the data begin in relation to the start
    // of the raw buffer
    const auto offset = _builder.GetBufferPointer() - _buffer.raw_begin();
    _buffer.set_body_endoffset(_buffer.preamble_size() + _buffer.body_capacity());
    _buffer.set_body_beginoffset(offset);
  }

  std::vector<flatbuffers::Offset<EnvelopeBytes>> _event_offsets;
  rl::flatbuffer_allocator _allocator;
  flatbuffers::FlatBufferBuilder _builder;
  buffer_t& _buffer;
};


template <typename TEvent, class TSerializer>
void Serialize(size_t context_size_kb, size_t ring_size, size_t buffer_size, size_t iterations)
{
  std::vector<TEvent> events(ring_size, Generate<TEvent>(context_size_kb));
  size_t current = 0;
  for (size_t i = 0; i < iterations; ++i) {
    rl::utility::data_buffer buffer;
    TSerializer collection_serializer(buffer);
    for (size_t j = 0; j < ring_size; ++j) {
      collection_serializer.add(events[current]);
      current = (current + 1) % ring_size;
    }
    collection_serializer.finalize();
  }
}

void PerfTest(const std::string& tag, std::function<void()> f) {
  const auto t_start = std::chrono::high_resolution_clock::now();
  f();
  const auto t_end = std::chrono::high_resolution_clock::now();
  const auto t = std::chrono::duration_cast<std::chrono::microseconds>(t_end - t_start).count();
  std::cout << tag << ": " << t << " microseconds" << std::endl;
}

void MemoryTest() {

  {
    const auto buffer = GetMemoryTestLegacyOutcomeBuffer();
    std::cout << "Float outcome holder size: " << buffer.size() << std::endl;
  }
  {
    const auto buffer = GetMemoryTestLegacyCbEventBuffer(100);
    std::cout << "Legacy cb event size: " << buffer.size() << std::endl;
  }
  {
    const auto buffer = GetMemoryTestNewCbEventBuffer(100, false);
    std::cout << "New cb event (context only) size: " << buffer.size() << std::endl;
  }
  {
    const auto buffer = GetMemoryTestNewCbEventBuffer(0, true);
    std::cout << "New cb event (outcome only) size: " << buffer.size() << std::endl;
  }
  {
    const auto buffer = GetMemoryTestNewCbEventBuffer(100, true);
    std::cout << "New cb event (context + outcome) size: " << buffer.size() << std::endl;
  }
}

void EnvelopeTest() {
  {
    PerfTest("Legacy serialization perf", []() { return Serialize<rl::ranking_event, rl::logger::fb_collection_serializer<rl::ranking_event>>(128, 32, 1024, 1024); });
  }

  {
    PerfTest("Union serialization perf", []() { return Serialize<rl::ranking_event, union_serializer>(128, 32, 1024, 1024); });
  }

  {
    PerfTest("Union serialization perf", []() { return Serialize<bytes_payload_event, bytes_serializer>(128, 32, 1024, 1024); });
  }
}


int main(int argc, char** argv) {
  try {
    MemoryTest();
    EnvelopeTest();
  }
  catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl;
    return -1;
  }
}
