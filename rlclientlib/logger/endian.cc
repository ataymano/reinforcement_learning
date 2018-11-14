#include "endian.h"

namespace reinforcement_learning{namespace logger{

    bool endian::is_big_endian(void)
    {
        const union {
            uint32_t i;
            char c[4];
        } b_int{0x01000000};
        return b_int.c[0] == 1;
    }

    uint32_t endian::htonl(uint32_t host_l)
    {
        if (is_big_endian())
        {
            return host_l;
        }
        uint32_t ret_val;
        uint8_t *p_ret_raw = (uint8_t *)&ret_val;
        uint8_t *p_raw = (uint8_t *)&host_l;
        p_ret_raw[0] = p_raw[3];
        p_ret_raw[1] = p_raw[2];
        p_ret_raw[2] = p_raw[1];
        p_ret_raw[3] = p_raw[0];
        return ret_val;
    }

    uint16_t endian::htons(uint16_t host_l)
    {
        if (is_big_endian())
        {
            return host_l;
        }
        uint16_t ret_val;
        uint8_t *p_ret_raw = (uint8_t *)&ret_val;
        uint8_t *p_raw = (uint8_t *)&host_l;
        p_ret_raw[0] = p_raw[1];
        p_ret_raw[1] = p_raw[0];
        return ret_val;
    }

    uint32_t endian::ntohl(uint32_t net_l)
    {
        if (is_big_endian())
        {
            return net_l;
        }
        uint32_t ret_val;
        uint8_t *p_ret_raw = (uint8_t *)&ret_val;
        uint8_t *p_raw = (uint8_t *)&net_l;
        p_ret_raw[0] = p_raw[3];
        p_ret_raw[1] = p_raw[2];
        p_ret_raw[2] = p_raw[1];
        p_ret_raw[3] = p_raw[0];
        return ret_val;
    }

    uint16_t endian::ntohs(uint16_t net_s)
    {
        if (is_big_endian())
        {
            return net_s;
        }
        uint16_t ret_val;
        uint8_t *p_ret_raw = (uint8_t *)&ret_val;
        uint8_t *p_raw = (uint8_t *)&net_s;
        p_ret_raw[0] = p_raw[1];
        p_ret_raw[1] = p_raw[0];
        return ret_val;
    }

} // namespace logger
} // namespace reinforcement_learning
