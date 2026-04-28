/**
 * BMS Monitor - Battery Management System Monitor
 *
 * Monitors 63S1P LiFePO4 battery pack via CAN bus.
 * Specs: ~200V system, 60kWh, 300Ah
 */

#ifndef BMS_MONITOR_H
#define BMS_MONITOR_H

#include <cstdint>
#include <mutex>
#include "../can_bus/can_interface.h"
#include "../can_bus/can_protocol.h"
#include "../../include/usv_control/usv_types.h"

class BMSMonitor {
public:
    BMSMonitor(CANInterface *can);

    /* Update from CAN frame */
    void updateStatus(const CANFrame *frame);

    /* Get current BMS state */
    BMSState getState() const;

    /* Check if battery is safe for operation */
    bool isSafe() const;

    /* Get max allowed discharge current */
    float getMaxDischargeCurrent() const;

    /* Get estimated remaining time (seconds) */
    float getRemainingTime() const;

private:
    CANInterface *can_;
    BMSState state_;
    mutable std::mutex mutex_;
};

#endif /* BMS_MONITOR_H */
