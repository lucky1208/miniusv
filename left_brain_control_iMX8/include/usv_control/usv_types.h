/**
 * USV Right Brain - Common Type Definitions
 *
 * Shared types for i.MX8 real-time control system.
 */

#ifndef USV_TYPES_H
#define USV_TYPES_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ========== Math Types ========== */

typedef struct {
    float x;
    float y;
    float z;
} Vec3f;

typedef struct {
    float x, y, z, w;
} Quatf;

typedef struct {
    float roll;   /* rad */
    float pitch;  /* rad */
    float yaw;    /* rad */
} EulerAngles;

/* ========== Navigation State ========== */

typedef struct {
    double lat;          /* degrees */
    double lon;          /* degrees */
    float  alt;          /* meters */
    float  accuracy;     /* meters */
    float  speed;        /* m/s */
    float  heading;      /* rad from North */
    bool   valid;
    uint64_t timestamp_ns;
} GPSData;

typedef struct {
    EulerAngles attitude;    /* roll, pitch, yaw (rad) */
    Vec3f angular_rate;      /* wx, wy, wz (rad/s) */
    Vec3f acceleration;      /* ax, ay, az (m/s²) */
    bool valid;
    uint64_t timestamp_ns;
} INSData;

/* ========== Motor State ========== */

typedef struct {
    float rpm;           /* current RPM */
    float current_a;     /* current (Amps) */
    float voltage_v;     /* voltage (V) */
    float temp_c;        /* temperature (°C) */
    float duty_cycle;    /* 0.0 - 1.0 */
    uint32_t fault_code; /* 0 = OK */
    bool enabled;
} MotorState;

typedef struct {
    MotorState left;
    MotorState right;
    uint64_t timestamp_ns;
} DualMotorState;

/* ========== BMS State ========== */

typedef struct {
    float pack_voltage;       /* V */
    float pack_current;       /* A (positive=discharge) */
    float soc;                /* 0-100% */
    float soh;                /* 0-100% */
    float max_cell_temp;      /* °C */
    float min_cell_voltage;   /* V */
    float max_cell_voltage;   /* V */
    float remaining_range_m;  /* meters */
    uint32_t fault_code;      /* 0 = OK */
    bool charging;
    uint64_t timestamp_ns;
} BMSState;

/* ========== Control Commands ========== */

typedef struct {
    float speed;       /* m/s (positive=forward) */
    float heading;     /* rad from North */
    float yaw_rate;    /* rad/s */
    uint8_t mode;      /* 0=idle, 1=auto, 2=manual, 3=emergency */
} ControlCommand;

typedef struct {
    float left_thrust;   /* -1.0 to 1.0 */
    float right_thrust;  /* -1.0 to 1.0 */
    float left_nozzle;   /* -1.0 to 1.0 (steering) */
    float right_nozzle;  /* -1.0 to 1.0 */
} JetThrustCommand;

/* ========== Operating Modes ========== */

typedef enum {
    MODE_IDLE = 0,
    MODE_AUTO = 1,
    MODE_MANUAL = 2,
    MODE_PATROL = 3,
    MODE_INTERCEPT = 4,
    MODE_RETURN = 5,
    MODE_EMERGENCY = 6,
} OperatingMode;

/* ========== System Health ========== */

typedef struct {
    float cpu_temp_c;
    float cpu_usage_pct;
    float mem_usage_pct;
    uint32_t uptime_s;
    uint32_t can_errors;
    uint32_t bridge_errors;
    bool healthy;
} SystemHealth;

#ifdef __cplusplus
}
#endif

#endif /* USV_TYPES_H */
