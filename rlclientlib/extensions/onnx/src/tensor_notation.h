#pragma once

#include "api_status.h"

#include <algorithm>
#include <string>
#include <vector>

#include <core/session/onnxruntime_cxx_api.h>

namespace reinforcement_learning { namespace onnx {
  using bytes_t = std::vector<unsigned char>;
  using tensor_data_t = std::pair<bytes_t, bytes_t>;

  /**
   * Check whether the provided bytes contain enough data to represent an
   * array of elements of type element_t
   */
  template <typename element_t>
  inline bool check_array_size(const bytes_t& bytes, size_t& element_count)
  {
    element_count = bytes.size() / sizeof(element_t);
    
    // The number of bytes in the dimensions array does not fit evenly into an 
    // array of elements of type element_t
    return element_count * sizeof(element_t) == bytes.size();
  }

  /**
   * Check whether the provided bytes contains exactly expected_element_count
   * elements of type element_t
   */
  template <typename element_t>
  inline bool check_array_size(const bytes_t& bytes, size_t expected_element_count, size_t& element_count)
  {
    check_array_size<element_t>(bytes, element_count);

    return (element_count == expected_element_count);
  }

  // TODO: Support reading type information for the tensor (and later map/sequence)
  using value_t = float;

  class OnnxRtInputContext
  {
  public:
    OnnxRtInputContext(const Ort::AllocatorInfo& allocator_info) : _allocator_info{allocator_info}
    {}

  public:
    inline std::vector<const char*> input_names() const
    {
      // Note, this is only valid for the lifetime of OrtInputContext
      int count = 0;

      std::vector<const char*> result;
      result.reserve(input_count());

      std::for_each(_input_names.cbegin(), _input_names.cend(), 
        [&result, &count](const std::string& str)
        {
          result.push_back(str.c_str());
        });

      return result;
    }

    inline size_t input_count() const
    {
      return _inputs.size();
    }

    inline std::vector<Ort::Value> inputs() const
    {
      // TODO: enable non-float tensors (see tensor_notation.cc for hook location)
      int count = 0;
      std::vector<Ort::Value> result;
      result.reserve(input_count());

      bool succeeded = false;

      for (int i = 0; i < _inputs.size(); i++)
      {
        const tensor_data_t& tensor = _inputs[i];
        const bytes_t& dimensions_bytes = tensor.first;
        const bytes_t& values_bytes = tensor.second;
        
        // Unpack the dimensions
        size_t rank = dimensions_bytes.size() / sizeof(int64_t);
        if (!check_array_size<int64_t>(dimensions_bytes, rank))
        {
          // TODO: error
          break;
        }

        // TODO: Should we validate that dimensions are all positive numbers during model load?
        int64_t* dimensions = (int64_t*)dimensions_bytes.data();
        size_t expected_values_count = rank == 0 ? 0 : std::accumulate(dimensions, dimensions + rank, 1, std::multiplies<size_t>());

        // Unpack the data
        size_t values_count = 0;
        if (!check_array_size<value_t>(values_bytes, expected_values_count, values_count))
        {
          // TODO: error
          break;
        }

        value_t* values = (value_t*)values_bytes.data();
        result.push_back(std::move(Ort::Value::CreateTensor<value_t>(this->_allocator_info, values, values_count, dimensions, rank)));

        succeeded = true;
      }

      if (!succeeded)
      {
        return {};
      }

      return result;
    }

  public:
    inline void push_input(const std::string& input_name, const tensor_data_t& input)
    {
      _input_names.push_back(input_name);
      _inputs.push_back(input);
    }

  private:
    std::vector<std::string> _input_names{};
    std::vector<tensor_data_t> _inputs{};

    const Ort::AllocatorInfo& _allocator_info;
  };

  int read_tensor_notation(const char* tensor_notation, OnnxRtInputContext* input_context, api_status* status = nullptr);
}}