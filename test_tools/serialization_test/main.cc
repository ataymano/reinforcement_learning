#include "action_flags.h"
#include "api_status.h"
#include "ranking_event.h"
#include "time_helper.h"
#include "data_buffer.h"
#include "serialization/fb_serializer.h"
#include <flatbuffers/flatbuffers.h>
#include "logger/flatbuffer_allocator.h"
#include "generated/TestEvent1_generated.h"
#include "generated/TestEvent2_generated.h"
#include "generated/CbEvent_generated.h"
#include "generated/CbOutcome_generated.h"
#include <boost/program_options.hpp>

#include <thread>

#include <iostream>

namespace po = boost::program_options;
namespace rl = reinforcement_learning;
namespace u=rl::utility;

using payload_t = std::vector<uint8_t>;

std::string generate_string(size_t kb) {
  const size_t size = kb * 1024;
  std::vector<char> buffer(size, '1');
  return std::string(&buffer[0], size);
}

std::vector<unsigned char> generate_byte_array(size_t kb) {
  const size_t size = kb * 1024;
  return std::vector<unsigned char>(size, '1');
}

/*payload_t serialize_TestEvt1() {
    flatbuffers::FlatBufferBuilder fbb(1024);
    auto serialized = CreateTestEvent1(fbb, 12);
    fbb.Finish(serialized);
    const auto result = payload_t(fbb.GetBufferPointer(), fbb.GetBufferPointer() + fbb.GetSize());
    return result;
}

const TestEvent1* deserialize_Evt1(payload_t serialized) {
    return GetTestEvent1((void*)(&serialized[0]));
}

void AssertTestEvent1() {
  const auto buffer = serialize_TestEvt1();
  const TestEvent1* ptr(deserialize_Evt1(buffer));
  std::cout << ptr->Field1() << std::endl;
}*/

payload_t SerializeFloatOutcomeHolder() {
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

const OutcomeEventHolder* deserialize_FloatOutcomeHolder(payload_t serialized) {
    return GetOutcomeEventHolder((void*)(&serialized[0]));
}

flatbuffers::Offset<RankingEvent2> CreateRankingEvent(size_t payload_size_kb, flatbuffers::FlatBufferBuilder& fbb) {
  const auto action_offset = fbb.CreateVector(std::vector<uint64_t> {1, 2, 3, 4, 5});
  const auto probabilities_offset = fbb.CreateVector(std::vector<float> {0.2, 0.2, 0.2, 0.2, 0.2});
  const auto context_offset = fbb.CreateVector(generate_byte_array(payload_size_kb));
  const auto model_id_offset = fbb.CreateString("model-id");

  return CreateRankingEvent2(fbb, true, action_offset, context_offset, probabilities_offset, model_id_offset);
}

flatbuffers::Offset<void> CreateNumericOutcome2(flatbuffers::FlatBufferBuilder& fbb) {
  return CreateNumericEvent2(fbb, 8).Union();
}

payload_t serialize_CbEventWithFloatOutcomeOnly(int context_size_kb) {
    flatbuffers::FlatBufferBuilder fbb(1024);
    const auto event_id = fbb.CreateString("event_id");
    TimeStamp client_ts(2020, 1, 2, 3, 4, 5, 6);
	  const auto meta_id_offset = CreateMetadata(fbb, &client_ts);
    auto retval = CreateCbEvent(fbb, event_id, 0.5, meta_id_offset, context_size_kb > 0 ? CreateRankingEvent(context_size_kb, fbb) : 0, OutcomeEvent2_NumericEvent2,
                                            CreateNumericOutcome2(fbb));

    fbb.Finish(retval);
    const auto result = payload_t(fbb.GetBufferPointer(), fbb.GetBufferPointer() + fbb.GetSize());
    return result;
}

const CbEvent* deserialize_CbEvent(payload_t serialized) {
    return GetCbEvent((void*)(&serialized[0]));
}

void CbEventMemoryTest() {
  {
    const auto buffer = SerializeFloatOutcomeHolder();
    std::cout << "Float outcome holder  size:" << buffer.size() << std::endl;

    const OutcomeEventHolder* ptr(deserialize_FloatOutcomeHolder(buffer));
    std::cout << ptr->event_id()->c_str() << std::endl;
  }
  //Reward 
  //Ranking event witth reward
  {
    const auto buffer = serialize_CbEventWithFloatOutcomeOnly(100);
    std::cout << "Cb event with float float outcome size:" << buffer.size() << std::endl;

    const CbEvent* ptr(deserialize_CbEvent(buffer));
    std::cout << ptr->event_id()->c_str() << std::endl;
  }
  //
}



/*static int serialize(outcome_event& evt, flatbuffers::FlatBufferBuilder& builder,
                         flatbuffers::Offset<fb_event_t>& retval, api_status* status) {
      const auto event_id = builder.CreateString(evt.get_event_id());
	  const auto &ts = evt.get_client_time_gmt();
	  TimeStamp client_ts(ts.year, ts.month, ts.day, ts.hour,
		  ts.minute, ts.second, ts.sub_second);
	  const auto meta_id_offset = CreateMetadata(builder, &client_ts);
	  switch (evt.get_outcome_type()) {
        case outcome_event::outcome_type_string: {
          const auto outcome_str = builder.CreateString(evt.get_outcome());
          const auto str_event = CreateStringEvent(builder, outcome_str).Union();
          retval = CreateOutcomeEventHolder(builder, event_id, evt.get_pass_prob(), OutcomeEvent_StringEvent,
                                            str_event, meta_id_offset);
          break;
        }
        case outcome_event::outcome_type_numeric: {
          const auto number_event = CreateNumericEvent(builder, evt.get_numeric_outcome()).Union();
          retval = CreateOutcomeEventHolder(builder, event_id, evt.get_pass_prob(), OutcomeEvent_NumericEvent,
                                            number_event, meta_id_offset);
          break;
        }
        case outcome_event::outcome_type_action_taken: {
          const auto action_taken_event = CreateActionTakenEvent(builder, evt.get_action_taken()).Union();
          retval = CreateOutcomeEventHolder(builder, event_id, evt.get_pass_prob(), OutcomeEvent_ActionTakenEvent,
                                            action_taken_event, meta_id_offset);
          break;
        }
        default: {
          return report_error(status, error_code::serialize_unknown_outcome_type,
                              error_code::serialize_unknown_outcome_type_s);
        }
      }
      return error_code::success;


struct test_serializer {
  using fb_event_t = Event;
  using offset_vector_t = typename std::vector<flatbuffers::Offset<fb_event_t>>;
  using batch_builder_t = EventBatchBuilder;

  static int serialize(flatbuffers::FlatBufferBuilder& builder,
    flatbuffers::Offset<fb_event_t>& ret_val) {
    const auto event_id_offset = builder.CreateString(evt.get_event_id());
    const auto action_ids_vector_offset = builder.CreateVector(evt.get_action_ids());
    const auto probabilities_vector_offset = builder.CreateVector(evt.get_probabilities());
    const auto context_offset = builder.CreateVector(evt.get_context());
    const auto model_id_offset = builder.CreateString(evt.get_model_id());
    const auto& ts = evt.get_client_time_gmt();
    TimeStamp client_ts(ts.year, ts.month, ts.day, ts.hour,
      ts.minute, ts.second, ts.sub_second);
    const auto meta_id_offset = CreateMetadata(builder, &client_ts);
    ret_val = CreateRankingEvent(builder, event_id_offset, evt.get_defered_action(), action_ids_vector_offset,
      context_offset, probabilities_vector_offset, model_id_offset,
      evt.get_pass_prob(), meta_id_offset);
    return error_code::success;
  }
};*/

/*template <typename event_t>
struct fb_collection_serializer {
  using serializer_t = fb_event_serializer<event_t>;
  using buffer_t = utility::data_buffer;
  static int message_id() { return message_type::UNKNOWN; }

  fb_collection_serializer(buffer_t& buffer)
    : _allocator(buffer), _builder(buffer.body_capacity(), &_allocator), _buffer(buffer) {}

  int add(event_t& evt, api_status* status = nullptr) {
    flatbuffers::Offset<typename serializer_t::fb_event_t> offset;
    RETURN_IF_FAIL(serializer_t::serialize(evt, _builder, offset, status));
    _event_offsets.push_back(offset);
    return error_code::success;
  }

  uint64_t size() const { return _builder.GetSize(); }

  void finalize() {
    auto event_offsets = _builder.CreateVector(_event_offsets);
    typename serializer_t::batch_builder_t batch_builder(_builder);
    batch_builder.add_events(event_offsets);
    auto batch_offset = batch_builder.Finish();
    _builder.Finish(batch_offset);
    // Where does the body of the data begin in relation to the start
    // of the raw buffer
    const auto offset = _builder.GetBufferPointer() - _buffer.raw_begin();
    _buffer.set_body_endoffset(_buffer.preamble_size() + _buffer.body_capacity());
    _buffer.set_body_beginoffset(offset);
  }

  typename serializer_t::offset_vector_t _event_offsets;
  flatbuffer_allocator _allocator;
  flatbuffers::FlatBufferBuilder _builder;
  buffer_t& _buffer;
};
*/

template<typename TEvent>
TEvent generate(size_t) {
  throw "Not supported";
}

template<>
rl::ranking_event generate(size_t size) {
  rl::ranking_response rr;
  rr.set_event_id("event_id");
  rr.set_chosen_action_id(0);
  rr.set_model_id("model");
  rr.push_back(0, 0.8);
  rr.push_back(1, 0.2);
  return rl::ranking_event::choose_rank("event_id", generate_string(size).c_str(), rl::action_flags::DEFAULT, rr, rl::timestamp(), 0.5);
}

template <typename TEvent, template<typename> class TSerializer>
void serialization_perf_test(size_t context_size_kb, size_t ring_size, size_t buffer_size, size_t iterations)
{
  std::vector<TEvent> events(ring_size, generate<TEvent>(context_size_kb));
  size_t current = 0;
  for (size_t i = 0; i < iterations; ++i) {
    rl::utility::data_buffer buffer;
    TEvent evt;
    TSerializer<TEvent> collection_serializer(buffer);
    for (size_t j = 0; j < ring_size; ++j) {
      collection_serializer.add(events[current]);
      current = (current + 1) % ring_size;
    }
    collection_serializer.finalize();
  }
}

template <typename TEvent, template<typename> class TSerializer>
void deserialization_perf_test(size_t context_size_kb, size_t ring_size, size_t buffer_size, size_t iterations)
{
  std::vector<TEvent> events(ring_size, generate<TEvent>(context_size_kb));
  size_t current = 0;
  for (size_t i = 0; i < iterations; ++i) {
    rl::utility::data_buffer buffer;
    TEvent evt;
    TSerializer<TEvent> collection_serializer(buffer);
    for (size_t j = 0; j < ring_size; ++j) {
      collection_serializer.add(events[current]);
      current = (current + 1) % ring_size;
    }
    collection_serializer.finalize();
  }
}

void test(const std::string& tag, std::function<void()> f) {
  const auto t_start = std::chrono::high_resolution_clock::now();
  f();
  const auto t_end = std::chrono::high_resolution_clock::now();
  const auto t = std::chrono::duration_cast<std::chrono::microseconds>(t_end - t_start).count();
  std::cout << tag << ": " << t << " microseconds" << std::endl;
}

po::variables_map process_cmd_line(const int argc, char** argv) {
  po::options_description desc("Options");
  desc.add_options()
    ("help", "produce help message")
    ("json_config,j", po::value<std::string>()->
      default_value("client.json"), "JSON file with config information for hosted RL loop")
    ("message_size,s", po::value<size_t>()->default_value(100), "Message size in Kb")
    ("message_count,n", po::value<size_t>()->default_value(1000000), "Amount of messages")
    ("threads,t", po::value<size_t>()->default_value(1))
    ;

  po::variables_map vm;
  store(parse_command_line(argc, argv, desc), vm);

  return vm;
}



int main(int argc, char** argv) {
  try {
    CbEventMemoryTest();
 //   const auto vm = process_cmd_line(argc, argv);
  //  test("ranking_event", []() { return serialization_perf_test<rl::ranking_event, rl::logger::fb_collection_serializer>(1, 1024, 30, 100); });
  }
  catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl;
    return -1;
  }
}
