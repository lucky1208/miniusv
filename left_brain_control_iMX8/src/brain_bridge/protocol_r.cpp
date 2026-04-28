/**
 * Right Brain Protocol Implementation
 *
 * Simple JSON encode/decode compatible with Left Brain Python protocol.
 * Uses minimal JSON formatting for embedded efficiency.
 */

#include "protocol_r.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>

/* CRC16-CCITT */
static uint16_t crc16_ccitt(const uint8_t *data, int len) {
    uint16_t crc = 0xFFFF;
    for (int i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc;
}

int usv_protocol_encode(const USVProtocolMsg &msg, char *buffer, int buf_size) {
    const char *type_name = "";
    char payload[2048] = {0};

    switch (msg.msg_type) {
    case USV_MSG_COMMAND_SPEED_HEADING:
        type_name = "COMMAND_SPEED_HEADING";
        snprintf(payload, sizeof(payload),
            "{\"speed\":%.3f,\"heading\":%.4f,\"yaw_rate\":%.4f,\"mode\":%u}",
            msg.payload.cmd_speed_heading.speed,
            msg.payload.cmd_speed_heading.heading,
            msg.payload.cmd_speed_heading.yaw_rate,
            msg.payload.cmd_speed_heading.mode);
        break;
    case USV_MSG_STATE_MOTORS:
        type_name = "STATE_MOTORS";
        snprintf(payload, sizeof(payload),
            "{\"left_rpm\":%.1f,\"right_rpm\":%.1f,\"left_current\":%.2f,\"right_current\":%.2f,"
            "\"left_temp\":%.1f,\"right_temp\":%.1f,\"left_fault\":%u,\"right_fault\":%u}",
            msg.payload.motor_state.left_rpm, msg.payload.motor_state.right_rpm,
            msg.payload.motor_state.left_current, msg.payload.motor_state.right_current,
            msg.payload.motor_state.left_temp, msg.payload.motor_state.right_temp,
            msg.payload.motor_state.left_fault, msg.payload.motor_state.right_fault);
        break;
    case USV_MSG_STATE_BMS:
        type_name = "STATE_BMS";
        snprintf(payload, sizeof(payload),
            "{\"voltage\":%.1f,\"current\":%.1f,\"soc\":%.1f,\"soh\":%.1f,"
            "\"max_cell_temp\":%.1f,\"fault_code\":%u,\"remaining_range\":%.0f}",
            msg.payload.bms_state.voltage, msg.payload.bms_state.current,
            msg.payload.bms_state.soc, msg.payload.bms_state.soh,
            msg.payload.bms_state.max_cell_temp, msg.payload.bms_state.fault_code,
            msg.payload.bms_state.remaining_range);
        break;
    case USV_MSG_STATE_SENSORS:
        type_name = "STATE_SENSORS";
        snprintf(payload, sizeof(payload),
            "{\"gps_lat\":%.7f,\"gps_lon\":%.7f,\"gps_alt\":%.2f,\"gps_accuracy\":%.2f,"
            "\"ins_roll\":%.4f,\"ins_pitch\":%.4f,\"ins_yaw\":%.4f,"
            "\"ins_wx\":%.4f,\"ins_wy\":%.4f,\"ins_wz\":%.4f}",
            msg.payload.sensor_state.gps_lat, msg.payload.sensor_state.gps_lon,
            msg.payload.sensor_state.gps_alt, msg.payload.sensor_state.gps_accuracy,
            msg.payload.sensor_state.ins_roll, msg.payload.sensor_state.ins_pitch,
            msg.payload.sensor_state.ins_yaw,
            msg.payload.sensor_state.ins_wx, msg.payload.sensor_state.ins_wy,
            msg.payload.sensor_state.ins_wz);
        break;
    case USV_MSG_HEARTBEAT:
        type_name = "HEARTBEAT";
        snprintf(payload, sizeof(payload), "{\"source\":%u}", msg.payload.heartbeat.source);
        break;
    case USV_MSG_EMERGENCY_STOP:
        type_name = "EMERGENCY_STOP";
        snprintf(payload, sizeof(payload), "{}");
        break;
    default:
        return 0;
    }

    /* Compute CRC */
    uint16_t crc = crc16_ccitt((const uint8_t *)payload, strlen(payload));

    /* Format full message */
    double ts = (double)usv_get_time_us() / 1000000.0;
    int len = snprintf(buffer, buf_size,
        "{\"msg_type\":\"%s\",\"timestamp\":%.3f,\"seq\":0,\"payload\":%s,\"crc16\":%u}",
        type_name, ts, payload, crc);

    return (len > 0 && len < buf_size) ? len : 0;
}

/* Simple JSON value extractor (minimal, for embedded use) */
static bool json_get_float(const char *json, const char *key, float *out) {
    char search[64];
    snprintf(search, sizeof(search), "\"%s\":", key);
    const char *p = strstr(json, search);
    if (!p) return false;
    p += strlen(search);
    while (*p == ' ') p++;
    *out = strtof(p, NULL);
    return true;
}

static bool json_get_double(const char *json, const char *key, double *out) {
    char search[64];
    snprintf(search, sizeof(search), "\"%s\":", key);
    const char *p = strstr(json, search);
    if (!p) return false;
    p += strlen(search);
    while (*p == ' ') p++;
    *out = strtod(p, NULL);
    return true;
}

static bool json_get_int(const char *json, const char *key, int *out) {
    char search[64];
    snprintf(search, sizeof(search), "\"%s\":", key);
    const char *p = strstr(json, search);
    if (!p) return false;
    p += strlen(search);
    while (*p == ' ') p++;
    *out = (int)strtol(p, NULL, 10);
    return true;
}

USVProtocolMsg usv_protocol_decode(const char *buffer, int length) {
    USVProtocolMsg msg;
    memset(&msg, 0, sizeof(msg));
    msg.valid = false;

    /* Determine message type */
    if (strstr(buffer, "\"COMMAND_SPEED_HEADING\"")) {
        msg.msg_type = USV_MSG_COMMAND_SPEED_HEADING;
        json_get_float(buffer, "speed", &msg.payload.cmd_speed_heading.speed);
        json_get_float(buffer, "heading", &msg.payload.cmd_speed_heading.heading);
        json_get_float(buffer, "yaw_rate", &msg.payload.cmd_speed_heading.yaw_rate);
        int mode = 0;
        json_get_int(buffer, "mode", &mode);
        msg.payload.cmd_speed_heading.mode = (uint8_t)mode;
        msg.valid = true;
    }
    else if (strstr(buffer, "\"EMERGENCY_STOP\"")) {
        msg.msg_type = USV_MSG_EMERGENCY_STOP;
        msg.valid = true;
    }
    else if (strstr(buffer, "\"HEARTBEAT\"")) {
        msg.msg_type = USV_MSG_HEARTBEAT;
        msg.valid = true;
    }

    return msg;
}
