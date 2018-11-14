#pragma once

#include <cstdint>
#include "api_status.h"
namespace reinforcement_learning {namespace utility {
  class data_buffer;
}}
namespace reinforcement_learning { namespace logger {
  class i_message_sender{
  public:
    virtual ~i_message_sender() = default;
    virtual int send(const uint16_t msg_type, utility::data_buffer& db) = 0;
    virtual int init(api_status* status) = 0;
  };
}}
