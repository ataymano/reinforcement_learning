#include "preamble_sender.h"
#include "preamble.h"

namespace reinforcement_learning {
  namespace logger {
    struct preamble;

    preamble_message_sender::preamble_message_sender(i_sender* sender) :_sender{sender} {}

    int preamble_message_sender::send(const uint16_t msg_type, utility::data_buffer& db) {
      // Set the preamble for this message
      preamble pre;
      pre.msg_type = msg_type;
      pre.msg_size = db.body_size();
      uint8_t *buffer;
      db.preamble(preamble::size(), buffer);
      pre.write_to_bytes(buffer);

      // Send message with preamble
      return _sender->send(buffer, db.body_size() + db.preamble_size());
    }

    int preamble_message_sender::init(api_status* status) {
      return _sender->init(status);
    }
  }
}
