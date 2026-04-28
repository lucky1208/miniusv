/**
 * CAN Protocol Definitions for USV
 *
 * CAN ID allocation:
 * 0x200-0x20F: ESC Motor Controllers (left=0x200, right=0x201)
 * 0x300-0x30F: BMS (main=0x300)
 * 0x400-0x40F: GPS/RTK Receiver
 * 0x500-0x50F: INS/IMU
 * 0x600-0x60F: System Control
 */

#ifndef CAN_PROTOCOL_H
#define CAN_PROTOCOL_H

#include <stdint.h>

/* ========== CAN IDs ========== */

/* ESC Motor Controllers */
#define CAN_ID_ESC_LEFT_TX      0x200   /* Command to left ESC */
#define CAN_ID_ESC_LEFT_RX      0x201   /* Status from left ESC */
#define CAN_ID_ESC_RIGHT_TX     0x202   /* Command to right ESC */
#define CAN_ID_ESC_RIGHT_RX     0x203   /* Status from right ESC */

/* BMS */
#define CAN_ID_BMS_STATUS       0x300   /* BMS status broadcast */
#define CAN_ID_BMS_CELL_DATA    0x301   /* Cell voltage/temperature */
#define CAN_ID_BMS_COMMAND      0x302   /* BMS command */

/* GPS/RTK */
#define CAN_ID_GPS_POSITION     0x400   /* Position data */
#define CAN_ID_GPS_VELOCITY     0x401   /* Velocity data */
#define CAN_ID_GPS_STATUS       0x402   /* GPS status/accuracy */

/* INS/IMU */
#define CAN_ID_INS_ATTITUDE     0x500   /* Roll, Pitch, Yaw */
#define CAN_ID_INS_GYRO         0x501   /* Angular rates */
#define CAN_ID_INS_ACCEL        0x502   /* Acceleration */

/* System */
#define CAN_ID_SYS_HEARTBEAT    0x600   /* System heartbeat */
#define CAN_ID_SYS_COMMAND      0x601   /* System command */
#define CAN_ID_SYS_CONFIG       0x602   /* Configuration */

/* ========== ESC Command Frame (8 bytes) ========== */
/*
 * Byte 0-1: Throttle (0-65535, 32767 = 0%)
 * Byte 2-3: Steering nozzle (-32768 to 32767)
 * Byte 4:   Mode (0=disable, 1=speed, 2=torque)
 * Byte 5:   Direction (0=forward, 1=reverse)
 * Byte 6-7: Reserved
 */
typedef struct __attribute__((packed)) {
    uint16_t throttle;
    int16_t  nozzle;
    uint8_t  mode;
    uint8_t  direction;
    uint16_t reserved;
} ESCCommandFrame;

/* ========== ESC Status Frame (8 bytes) ========== */
/*
 * Byte 0-1: RPM
 * Byte 2-3: Current (0.1A)
 * Byte 4-5: Temperature (0.1°C, offset -40)
 * Byte 6:   Fault code
 * Byte 7:   Status flags
 */
typedef struct __attribute__((packed)) {
    uint16_t rpm;
    uint16_t current_01a;
    uint16_t temp_01c;
    uint8_t  fault_code;
    uint8_t  status_flags;
} ESCStatusFrame;

/* ========== BMS Status Frame (8 bytes) ========== */
/*
 * Byte 0-1: Pack voltage (0.1V)
 * Byte 2-3: Pack current (0.1A, signed)
 * Byte 4:   SOC (0-100%)
 * Byte 5:   SOH (0-100%)
 * Byte 6:   Max cell temp (°C, offset -40)
 * Byte 7:   Fault code
 */
typedef struct __attribute__((packed)) {
    uint16_t voltage_01v;
    int16_t  current_01a;
    uint8_t  soc_pct;
    uint8_t  soh_pct;
    uint8_t  max_cell_temp_c;
    uint8_t  fault_code;
} BMSStatusFrame;

/* ========== GPS Position Frame (8 bytes) ========== */
/*
 * Byte 0-3: Latitude (1e-7 degrees, signed)
 * Byte 4-7: Longitude (1e-7 degrees, signed)
 */
typedef struct __attribute__((packed)) {
    int32_t lat_1e7;
    int32_t lon_1e7;
} GPSPositionFrame;

/* ========== INS Attitude Frame (8 bytes) ========== */
/*
 * Byte 0-1: Roll (0.01°, signed)
 * Byte 2-3: Pitch (0.01°, signed)
 * Byte 4-5: Yaw (0.01°, signed)
 * Byte 6-7: Timestamp (ms, modulo 65536)
 */
typedef struct __attribute__((packed)) {
    int16_t roll_001deg;
    int16_t pitch_001deg;
    int16_t yaw_001deg;
    uint16_t timestamp_ms;
} INSAttitudeFrame;

/* ========== Helper Functions ========== */

static inline void esc_cmd_to_bytes(const ESCCommandFrame *cmd, uint8_t *data) {
    memcpy(data, cmd, 8);
}

static inline void esc_status_from_bytes(const uint8_t *data, ESCStatusFrame *status) {
    memcpy(status, data, 8);
}

static inline void bms_status_from_bytes(const uint8_t *data, BMSStatusFrame *status) {
    memcpy(status, data, 8);
}

static inline void gps_pos_from_bytes(const uint8_t *data, GPSPositionFrame *pos) {
    memcpy(pos, data, 8);
}

static inline void ins_att_from_bytes(const uint8_t *data, INSAttitudeFrame *att) {
    memcpy(att, data, 8);
}

#endif /* CAN_PROTOCOL_H */
