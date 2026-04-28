/**
 * Right Brain Protocol - C implementation for i.MX8
 *
 * Lightweight JSON protocol compatible with Left Brain Python protocol.
 */

#ifndef PROTOCOL_R_H
#define PROTOCOL_R_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Message types (must match left_brain protocol.py) */
typedef enum {
    USV_MSG_COMMAND_SPEED_HEADING = 1,
    USV_MSG_COMMAND_MODE = 2,
    USV_MSG_EMERGENCY_STOP = 3,
    USV_MSG_STATE_MOTORS = 10,
    USV_MSG_STATE_BMS = 11,
    USV_MSG_STATE_SENSORS = 12,
    USV_MSG_HEARTBEAT = 20,
} USVMessageType;

/* Payload unions */
typedef struct {
    float speed;
    float heading;
    float yaw_rate;
    uint8_t mode;
} CmdSpeedHeading;

typedef struct {
    float left_rpm, right_rpm;
    float left_current, right_current;
    float left_temp, right_temp;
    uint32_t left_fault, right_fault;
} MotorStatePayload;

typedef struct {
    float voltage, current;
    float soc, soh;
    float max_cell_temp;
    uint32_t fault_code;
    float remaining_range;
} BMSPayload;

typedef struct {
    double gps_lat, gps_lon;
    float gps_alt, gps_accuracy;
    float ins_roll, ins_pitch, ins_yaw;
    float ins_wx, ins_wy, ins_wz;
} SensorPayload;

typedef struct {
    uint8_t source;
} HeartbeatPayload;

/* Full message */
typedef struct {
    USVMessageType msg_type;
    bool valid;
    union {
        CmdSpeedHeading cmd_speed_heading;
        MotorStatePayload motor_state;
        BMSPayload bms_state;
        SensorPayload sensor_state;
        HeartbeatPayload heartbeat;
    } payload;
} USVProtocolMsg;

/* Get monotonic time in microseconds */
static inline uint64_t usv_get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

/* Encode message to JSON buffer, return bytes written */
int usv_protocol_encode(const USVProtocolMsg &msg, char *buffer, int buf_size);

/* Decode message from JSON buffer */
USVProtocolMsg usv_protocol_decode(const char *buffer, int length);

#ifdef __cplusplus
}
#endif

#endif /* PROTOCOL_R_H */
