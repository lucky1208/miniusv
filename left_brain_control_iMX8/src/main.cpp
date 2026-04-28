/**
 * USV Left Brain (Control) Main Program (i.MX8)
 *
 * Real-time control loop running on i.MX8 industrial carrier board.
 * Responsible for:
 * - Motor control via CAN bus (50Hz)
 * - BMS monitoring (10Hz)
 * - Navigation sensor reading (50Hz)
 * - Attitude control (PID heading + speed) (50Hz)
 * - Communication with Right Brain (AI, Jetson Orin NX) via Ethernet
 * - Hardware watchdog
 *
 * Architecture:
 * ┌──────────────────────────────────────────────┐
 * │        Left Brain (Control) - i.MX8          │
 * │                                              │
 * │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
 * │  │ CAN Bus  │  │  Motor   │  │   BMS    │  │
 * │  │SocketCAN │→ │ Control  │  │ Monitor  │  │
 * │  └──────────┘  └──────────┘  └──────────┘  │
 * │        │              │            │         │
 * │  ┌──────────┐  ┌──────────────────────┐     │
 * │  │  Nav     │  │ Attitude Control     │     │
 * │  │ Sensors  │  │ PID + LQR            │     │
 * │  └──────────┘  └──────────────────────┘     │
 * │        │              │                      │
 * │  ┌──────────────────────────────────────┐   │
 * │  │  Brain Bridge ← Right Brain (AI)     │   │
 * │  │  (receives commands, sends status)   │   │
 * │  └──────────────────────────────────────┘   │
 * │  ┌──────────┐                               │
 * │  │ Watchdog │                               │
 * │  └──────────┘                               │
 * └──────────────────────────────────────────────┘
 */

#include <cstdio>
#include <cstring>
#include <cmath>
#include <csignal>
#include <unistd.h>
#include <time.h>

#include "can_bus/can_interface.h"
#include "motor_control/motor_manager.h"
#include "bms_monitor/bms_monitor.h"
#include "bms_monitor/power_manager.h"
#include "attitude_control/heading_controller.h"
#include "attitude_control/speed_controller.h"
#include "brain_bridge/brain_bridge_r.h"
#include "watchdog/watchdog.h"
#include "usv_control/usv_types.h"

/* Global running flag for signal handler */
static volatile bool g_running = true;

void signal_handler(int sig) {
    printf("\n[LeftBrain] Signal %d received, shutting down...\n", sig);
    g_running = false;
}

/* Get current time in seconds */
static double get_time_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

int main(int argc, char *argv[]) {
    printf("========================================\n");
    printf("  USV Left Brain (Control, i.MX8) v1.0.0\n");
    printf("  SeaBlade USV-4500 Control System\n");
    printf("========================================\n");

    /* Install signal handlers */
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    /* Initialize CAN bus */
    CANInterface can;
    if (can_init(&can, "can0", 500000) < 0) {
        printf("[ERROR] CAN bus init failed! Trying can1...\n");
        if (can_init(&can, "can1", 500000) < 0) {
            printf("[FATAL] No CAN interface available!\n");
            return -1;
        }
    }

    /* Initialize modules */
    MotorManager motor_mgr(&can);
    BMSMonitor bms_monitor(&can);
    PowerManager power_mgr(&bms_monitor);
    HeadingController heading_ctrl;
    SpeedController speed_ctrl;
    BrainBridgeR bridge("192.168.1.1", 9876);
    Watchdog watchdog;

    /* Start bridge */
    if (!bridge.start()) {
        printf("[WARN] Brain Bridge start failed - running standalone\n");
    }

    /* Start watchdog (10 second timeout) */
    watchdog.start(10);

    /* Enable motors */
    motor_mgr.setEnabled(true);

    /* Navigation state */
    GPSData gps = {};
    INSData ins = {};
    ControlCommand cmd = {};

    /* Control loop timing */
    const double CONTROL_PERIOD = 0.02;   /* 50Hz = 20ms */
    const double STATUS_PERIOD = 0.1;     /* 10Hz = 100ms */
    double last_control_time = get_time_s();
    double last_status_time = get_time_s();
    double last_watchdog_time = get_time_s();

    printf("[LeftBrain] Entering main control loop (50Hz)...\n");

    /* Main control loop */
    while (g_running) {
        double now = get_time_s();
        double dt = now - last_control_time;

        /* ---- 50Hz Control Loop ---- */
        if (dt >= CONTROL_PERIOD) {
            last_control_time = now;

            /* Get command from Right Brain (AI) */
            cmd = bridge.getCommand();

            /* Check for emergency */
            if (cmd.mode == 6) {  /* MODE_EMERGENCY */
                motor_mgr.emergencyStop();
                printf("[EMERGENCY] Motor emergency stop!\n");
                continue;
            }

            /* Check BMS safety */
            if (!bms_monitor.isSafe()) {
                printf("[WARN] BMS unsafe! Reducing power.\n");
                cmd.speed *= 0.5f;
            }

            /* Attitude control: compute yaw_rate from heading command */
            float yaw_rate = heading_ctrl.compute(
                cmd.heading, ins.attitude.yaw, (float)dt
            );

            /* Override yaw_rate if provided directly */
            if (std::fabs(cmd.yaw_rate) > 0.01f) {
                yaw_rate = cmd.yaw_rate;
            }

            /* Set motor command */
            ControlCommand motor_cmd = cmd;
            motor_cmd.yaw_rate = yaw_rate;
            motor_mgr.setCommand(motor_cmd);

            /* Update motor control */
            motor_mgr.update((float)dt);
        }

        /* ---- 10Hz Status Loop ---- */
        if (now - last_status_time >= STATUS_PERIOD) {
            last_status_time = now;

            /* Send motor state to Right Brain (AI) */
            DualMotorState motor_state = motor_mgr.getState();
            bridge.sendMotorState(motor_state);

            /* Send BMS state to Right Brain (AI) */
            BMSState bms_state = bms_monitor.getState();
            bridge.sendBMSState(bms_state);

            /* Send sensor state to Right Brain (AI) */
            bridge.sendSensorState(gps, ins);

            /* Periodic log */
            static int log_counter = 0;
            if (++log_counter >= 10) {  /* Every 1 second */
                log_counter = 0;
                printf("[Status] Speed cmd=%.1f m/s | Heading cmd=%.1f° | "
                       "SOC=%.0f%% | Voltage=%.1fV | Bridge=%s\n",
                       cmd.speed, cmd.heading * 180.0f / M_PI,
                       bms_state.soc, bms_state.pack_voltage,
                       bridge.isConnected() ? "OK" : "LOST");
            }
        }

        /* ---- Watchdog Kick (1Hz) ---- */
        if (now - last_watchdog_time >= 1.0) {
            last_watchdog_time = now;
            watchdog.kick();
        }

        /* Sleep to prevent busy-waiting (1ms precision) */
        usleep(1000);
    }

    /* Clean shutdown */
    printf("[LeftBrain] Shutting down...\n");
    motor_mgr.emergencyStop();
    motor_mgr.setEnabled(false);
    bridge.stop();
    can_close(&can);
    watchdog.stop();

    printf("[LeftBrain] Shutdown complete.\n");
    return 0;
}
