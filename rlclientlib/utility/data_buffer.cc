#include "data_buffer.h"
#include <string>
#include <iostream>

#include "err_constants.h"

namespace reinforcement_learning {
  namespace utility {

    data_buffer::data_buffer(size_t body_size, size_t preamble_size)
      : _buffer(body_size + preamble_size), _body_begin_offset{ preamble_size }, _preamble_size(preamble_size) {
    }

    void data_buffer::reset() {
      _body_begin_offset = _preamble_size;
      _body_write_pos = 0;
      _buffer.clear();
      _buffer.resize(_preamble_size);
    }

    unsigned char* data_buffer::raw_begin() {
      return _buffer.data();
    }

    size_t data_buffer::body_size() const {
      return _buffer.size() - _body_begin_offset;
    }

    size_t data_buffer::body_capacity() const {
      return _buffer.capacity() - _body_begin_offset;
    }

    void data_buffer::remove_last() { _buffer.pop_back(); }

    size_t data_buffer::get_body_offset() const {
      return _body_begin_offset;
    }

    int data_buffer::set_body_offset(size_t begin_offset) {
      if (begin_offset > _buffer.size()) {
        return error_code::invalid_argument;
      }

      _body_begin_offset = begin_offset;
      return error_code::success;
    }

    unsigned char* data_buffer::body() {
      return (_buffer.data()) + _body_begin_offset;
    }

    void data_buffer::resize(size_t size) {
      _buffer.resize(size + _preamble_size);
    }

    int data_buffer::preamble(uint32_t preamble_size, unsigned char*& p_preamble) {
      if (preamble_size != _preamble_size)
        return error_code::incorrect_buffer_preamble_size;

      p_preamble = _buffer.data() + (_body_begin_offset - _preamble_size);
      return error_code::success;
    }

    size_t data_buffer::preamble_size() const {
      return _preamble_size;
    }

    data_buffer& data_buffer::operator<<(const std::string& cs) {
      auto cs_size = cs.size();
      // ensure there is enough buffer so we don't reallocate during insert
      _buffer.reserve(body_size() + preamble_size() + cs_size);
      // copy the string to the buffer
      _buffer.insert(_buffer.begin() + preamble_size() + _body_write_pos, cs.begin(), cs.end());
      // Null terminate.  For example if the buffer is being reused, this 
      // guarantees that the body is null terminated
      _buffer.emplace_back(0);
      // Write body position is updated (not including the null terminator)
      _body_write_pos += cs_size;
      return *this;
    }

    data_buffer& data_buffer::operator<<(const char* data) { return operator<<(std::string(data)); }
    data_buffer& data_buffer::operator<<(size_t rhs) { return operator<<(std::to_string(rhs)); }
    data_buffer& data_buffer::operator<<(float rhs) { return operator<<(std::to_string(rhs)); }

    buffer_factory::buffer_factory() = default;

    data_buffer* buffer_factory::operator()() const {
      return new data_buffer();
    }
  }
}

