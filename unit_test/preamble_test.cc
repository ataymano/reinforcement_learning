#define BOOST_TEST_DYN_LINK
#ifdef STAND_ALONE
#   define BOOST_TEST_MODULE Main
#endif

#include <boost/test/unit_test.hpp>
#include "utility/data_buffer.h"

using namespace reinforcement_learning::utility;

struct i_message_sender {
  virtual ~i_message_sender() = default;
  virtual int send(const uint16_t msg_type, data_buffer& db) = 0;
};

struct endian {

  static bool is_big_endian(void) {
    const union {
      uint32_t i;
      char c[4];
    } b_int { 0x01000000 };
    return b_int.c[0] == 1;
  }

  static uint32_t htonl(uint32_t host_l) {
    if (is_big_endian()) {
      return host_l;
    }
    uint32_t ret_val;
    uint8_t* p_ret_raw = (uint8_t*)& ret_val;
    uint8_t* p_raw = (uint8_t*)& host_l;
    p_ret_raw[0] = p_raw[3];
    p_ret_raw[1] = p_raw[2];
    p_ret_raw[2] = p_raw[1];
    p_ret_raw[3] = p_raw[0];
    return ret_val;
  };

  static uint16_t htons(uint16_t host_l) {
    if (is_big_endian()) {
      return host_l;
    }
    uint16_t ret_val;
    uint8_t* p_ret_raw = (uint8_t*)& ret_val;
    uint8_t* p_raw = (uint8_t*)& host_l;
    p_ret_raw[0] = p_raw[1];
    p_ret_raw[1] = p_raw[0];
    return ret_val;
  };

  static uint32_t ntohl(uint32_t net_l) {
    if (is_big_endian()) {
      return net_l;
    }
    uint32_t ret_val;
    uint8_t* p_ret_raw = (uint8_t*)& ret_val;
    uint8_t* p_raw = (uint8_t*)& net_l;
    p_ret_raw[0] = p_raw[3];
    p_ret_raw[1] = p_raw[2];
    p_ret_raw[2] = p_raw[1];
    p_ret_raw[3] = p_raw[0];
    return ret_val;
  };

  static uint16_t ntohs(uint16_t net_s) {
    if (is_big_endian()) {
      return net_s;
    }
    uint16_t ret_val;
    uint8_t* p_ret_raw = (uint8_t*)& ret_val;
    uint8_t* p_raw = (uint8_t*)& net_s;
    p_ret_raw[0] = p_raw[1];
    p_ret_raw[1] = p_raw[0];
    return ret_val;
  };
};

struct preamble {
  uint8_t reserved;
  uint8_t version;
  uint16_t msg_type;
  uint32_t msg_size;

  preamble() : reserved{ 0 }, version{ 0 }, msg_type{ 0 }, msg_size{ 0 }{}

  static uint32_t byte_size() { return 8; };

  void write_to_bytes(uint8_t* buffer) {
    buffer[0] = reserved;
    buffer[1] = version;
    uint16_t* p_type = reinterpret_cast<uint16_t*>(buffer[2]);
    *p_type = endian::htons(msg_type);
    uint32_t* p_size = reinterpret_cast<uint32_t*>(buffer[4]);
    *p_size = endian::htonl(msg_size);
  }

  void read_from_bytes(uint8_t* buffer) {
    reserved = buffer[0];
    version = buffer[1];
    uint16_t* p_type = reinterpret_cast<uint16_t*>(buffer[2]);
    msg_type = endian::ntohs(*p_type);
    uint32_t* p_size = reinterpret_cast<uint32_t*>(buffer[4]);
    msg_size = endian::ntohl(*p_size);
  }
};

struct preamble_message_sender : i_message_sender {
  int send(const uint16_t msg_type, data_buffer& db) override {
    preamble pre;
    pre.msg_type = msg_type;
    pre.msg_size = db.size();
    uint8_t buffer[8];
    db.get_preamble(preamble::byte_size());
    pre.write_to_bytes(buffer);
    pre.read_from_bytes(buffer);
  }
};

struct message_type {
  using const_int = const uint16_t;
  // Flat buffer ranking event collection message
  static const_int fb_ranking_event_collection = 1;
};

BOOST_AUTO_TEST_CASE(simple_preamble_usage) {
  data_buffer db;

  preamble_message_sender f_sender;
  i_message_sender& sender = f_sender;

  sender.send(message_type::fb_ranking_event_collection, db);
}
