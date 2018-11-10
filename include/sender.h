#pragma once

#include <vector>

namespace reinforcement_learning {
  class api_status;

  class i_sender {
  public:
    virtual int init(api_status* status) = 0;

    int send(std::vector<unsigned char>&& data, api_status* status = nullptr) {
      return v_send(std::move(data), status);
    }

    int send(unsigned char* data, size_t size, api_status* status = nullptr) {
      return v_send(data, size, status);
    }

    virtual ~i_sender() = default;

  protected:
    virtual int v_send(std::vector<unsigned char>&& data, api_status* status) = 0;
    virtual int v_send(unsigned char* data, size_t size, api_status* status) = 0;
  };
}
