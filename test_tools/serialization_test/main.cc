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

void CbEventMemoryTest() {

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

int main(int argc, char** argv) {
  try {
    CbEventMemoryTest();
  }
  catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl;
    return -1;
  }
}
