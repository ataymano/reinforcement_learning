#pragma once
#include <string>
#include <vector>

namespace reinforcement_learning { namespace utility {

  /*
   * Data buffer used for serialized messages.  Data buffer
   * consists of 2 parts.  1) preamble 2) body
   */
  class data_buffer {
  public:
    explicit data_buffer(size_t body_size = 1024, size_t preamble_size = 8);

    // Get a pointer to beginning of preamble
    int preamble(uint32_t preamble_size, unsigned char*& p_preamble);

    // Get preamble size
    size_t preamble_size() const;

    // Return pointer to beginning of buffer, starting at offset from the real beginning.
    unsigned char* body();

    // Body size does not include the preamble.
    size_t body_size() const;

    //// Size is the total buffer size. (Note: this is not necessarily equal to std::vector capacity)
    size_t body_capacity() const;

    // Offset from beginning of buffer where the body starts
    size_t get_body_offset() const;

    // Offset from beginning of buffer where the body starts
    int set_body_offset(size_t begin_offset);
    
    // Remove the last byte
    void remove_last();

    // Will resize entire buffer
    void resize(size_t size);

    // Clear the contents of the buffer
    void reset();

    // Get the beginning of the raw buffer
    unsigned char* raw_begin();

    data_buffer& operator<<(const std::string& cs);
    data_buffer& operator<<(const char*);
    data_buffer& operator<<(size_t rhs);
    data_buffer& operator<<(float rhs);

  private:
    std::vector<unsigned char> _buffer;
    size_t _body_begin_offset = 0;
    size_t _preamble_size = 0;
    size_t _body_write_pos = 0;
  };

  class buffer_factory {
  public:
    buffer_factory();
    data_buffer* operator()() const;
  };
}}


