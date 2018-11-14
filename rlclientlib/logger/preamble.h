#pragma once
#include <cstdint>
#include "endian.h"

namespace reinforcement_learning { namespace logger {
    struct preamble {
      uint8_t reserved;
      uint8_t version;
      uint16_t msg_type;
      uint32_t msg_size;

      preamble() : reserved{ 0 }, version{ 0 }, msg_type{ 0 }, msg_size{ 0 }{}
      void write_to_bytes(uint8_t* buffer);
      void read_from_bytes(uint8_t* buffer);
      static uint32_t size() { return 8; };
    };
}}
