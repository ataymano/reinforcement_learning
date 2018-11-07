#include "flatbuffer_allocator.h"

namespace reinforcement_learning {
  flatbuffer_allocator::flatbuffer_allocator(utility::data_buffer& data_buffer)
    : _buffer(data_buffer)
  {
  }

  uint8_t* flatbuffer_allocator::allocate(size_t size)  {
    _buffer.resize(size);
    return _buffer.buffer().data();
  }

  void flatbuffer_allocator::deallocate(uint8_t *p, size_t size) {}

  uint8_t* flatbuffer_allocator::reallocate_downward(uint8_t *old_p, size_t old_size, size_t new_size, size_t in_use_back, size_t in_use_front) {
    return _buffer.buffer().data();
  }
}