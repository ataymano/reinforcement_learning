#include "preamble.h"

namespace reinforcement_learning { namespace logger {

    void preamble::write_to_bytes(uint8_t* buffer) {
        buffer[0] = reserved;
        buffer[1] = version;
        uint16_t* p_type = reinterpret_cast<uint16_t*>(buffer+2);
        *p_type = endian::htons(msg_type);
        uint32_t* p_size = reinterpret_cast<uint32_t*>(buffer+4);
        *p_size = endian::htonl(msg_size);
    }

    void preamble::read_from_bytes(uint8_t* buffer) {
        reserved = buffer[0];
        version = buffer[1];
        uint16_t* p_type = reinterpret_cast<uint16_t*>(buffer+2);
        msg_type = endian::ntohs(*p_type);
        uint32_t* p_size = reinterpret_cast<uint32_t*>(buffer+4);
        msg_size = endian::ntohl(*p_size);
    }

}}