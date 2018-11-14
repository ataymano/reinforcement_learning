#define BOOST_TEST_DYN_LINK
#ifdef STAND_ALONE
#   define BOOST_TEST_MODULE Main
#endif

#include <boost/test/unit_test.hpp>
#include "utility/data_buffer.h"

using namespace reinforcement_learning;
using namespace utility;
using namespace std;

BOOST_AUTO_TEST_CASE(new_data_buffer_is_empty) {
  data_buffer buffer;

  BOOST_CHECK_EQUAL(buffer.body_size(), 0);
}

BOOST_AUTO_TEST_CASE(single_output_to_data_buffer) {
  data_buffer buffer;

  buffer << "test";
  string body((char *)buffer.body());
  BOOST_CHECK_EQUAL(body, "test");
}

BOOST_AUTO_TEST_CASE(multiple_outputs_to_data_buffer) {
  data_buffer buffer;

  const string value_string = "test";
  const size_t value_size_t = 2;

  buffer << value_string << value_size_t << value_string.c_str();
  string body((char *)buffer.body());
  BOOST_CHECK_EQUAL(body, "test2test");
}

BOOST_AUTO_TEST_CASE(empty_data_buffer_reset) {
  data_buffer buffer;

  buffer.reset();
  BOOST_CHECK_EQUAL(buffer.body_size(), 0);
}

BOOST_AUTO_TEST_CASE(nonempty_data_buffer_reset) {
  data_buffer buffer;

  buffer << "test";
  buffer.reset();
  BOOST_CHECK_EQUAL(buffer.body_size(), 0);
}

BOOST_AUTO_TEST_CASE(data_buffer_reset_rewrite) {
  data_buffer buffer;

  buffer << "test";
  string body((char *)buffer.body());
  BOOST_CHECK_EQUAL(body, "test");
  buffer.reset();
  BOOST_CHECK_EQUAL(buffer.body_size(), 0);
  buffer << "tt";
  body = (char *)buffer.body();
  BOOST_CHECK_EQUAL(body, "tt");
}

BOOST_AUTO_TEST_CASE(data_buffer_binary) {
  
}


BOOST_AUTO_TEST_CASE(data_buffer_set_offset) {}
BOOST_AUTO_TEST_CASE(data_buffer_set_offset_too_large) {}
