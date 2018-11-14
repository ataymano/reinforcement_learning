#define BOOST_TEST_DYN_LINK
#ifdef STAND_ALONE
#   define BOOST_TEST_MODULE Main
#endif

#include <boost/test/unit_test.hpp>
#include "utility/data_buffer.h"
#include "logger/preamble_sender.h"
#include "logger/message_type.h"
#include "err_constants.h"
#include "logger/preamble.h"

using namespace reinforcement_learning::utility;
using namespace reinforcement_learning::logger;
using namespace reinforcement_learning;

struct dummy_sender : i_sender {
  int init(api_status* status) override {
    return error_code::success;
  };

  int v_send(std::vector<unsigned char>&& data, api_status* status) override {
    v_data = data;
    return error_code::success;
  };

  int v_send(unsigned char* data, size_t size, api_status* status) override {
    this->data = data;
    this->size = size;
    return error_code::success;
  };

  dummy_sender() : data(nullptr), size(0) {}

  unsigned char* data;
  size_t size;
  std::vector<unsigned char> v_data;
};

BOOST_AUTO_TEST_CASE(simple_preamble_usage) {
  data_buffer db;
  dummy_sender raw_data;
  preamble_message_sender f_sender(&raw_data);
  i_message_sender& sender = f_sender;

  auto send_msg_sz = db.body_size();
  auto send_msg_type = message_type::fb_ranking_event_collection;

  sender.send(send_msg_type, db);
  preamble pre;
  pre.read_from_bytes(raw_data.data);

  BOOST_CHECK_EQUAL(pre.msg_size, send_msg_sz);
  BOOST_CHECK_EQUAL(pre.msg_type, send_msg_type);
}
