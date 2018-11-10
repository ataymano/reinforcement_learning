#pragma once
#include <string>
#include <vector>

namespace reinforcement_learning { namespace utility {

  class data_buffer {
  public:
    data_buffer();
    void reset();

    // Return pointer to beginning of buffer, starting at offset from the real beginning.
    unsigned char* data() const;
    std::vector<unsigned char> buffer();

    // Size is capacity less the amount preceding begin.
    size_t size() const;

    // Size is the total buffer size. (Note: this is not necessarily equal to std::vector capacity)
    size_t capacity() const;

    // Offset from beginning of buffer.
    size_t offset() const;
    int set_begin_offset(size_t offset);

    void append(const unsigned char* data, size_t len);

    std::string str() const;
    void remove_last();

    // Will reserve entire buffer, ignoring offset.
    void reserve(size_t size);

    // Will resize entire buffer, ignoring offset. Undefined behavior will occur if the buffer is resized to less than the offset.
    void resize(size_t size);

    data_buffer& operator<<(const std::string& cs);
    data_buffer& operator<<(const char*);
    data_buffer& operator<<(size_t rhs);
    data_buffer& operator<<(float rhs);

    unsigned char* get_preamble(uint32_t byte_size);

  private:
    std::vector<unsigned char> _buffer;
    size_t _begin_offset = 0;
  };

  class buffer_factory {
  public:
    buffer_factory();
    data_buffer* operator()() const;
  };
}}


