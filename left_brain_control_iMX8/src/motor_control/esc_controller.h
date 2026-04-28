/**
 * ESC (Electronic Speed Controller) Controller
 *
 * Controls water-cooled BLDC motor controllers via CAN bus.
 * Each ESC drives one 25kW BLDC PMSM motor + Marine Jet pump.
 *
 * Specs (from design doc):
 * - 2x water-cooled BLDC ESC controllers
 * - Motor: 25kW BLDC PMSM per side
 * - Total power: 50kW
 * - System voltage: ~200V (63S1P battery pack)
 */

#ifndef ESC_CONTROLLER_H
#define ESC_CONTROLLER_H

#include <cstdint>
#include <mutex>
#include "../can_bus/can_interface.h"
#include "../can_bus/can_protocol.h"
#include "../../include/usv_control/usv_types.h"

class ESCController {
public:
    ESCController(CANInterface *can, uint32_t can_id_cmd, uint32_t can_id_status);

    /* Set throttle (0.0 - 1.0) */
    void setThrottle(float throttle);

    /* Set steering nozzle angle (-1.0 to 1.0) */
    void setNozzleAngle(float angle);

    /* Set direction (true = reverse) */
    void setReverse(bool reverse);

    /* Enable/disable motor */
    void setEnabled(bool enabled);

    /* Emergency stop */
    void emergencyStop();

    /* Update status from CAN frame */
    void updateStatus(const CANFrame *frame);

    /* Get current motor state */
    MotorState getState() const;

    /* Send current command to ESC via CAN */
    int sendCommand();

private:
    CANInterface *can_;
    uint32_t can_id_cmd_;
    uint32_t can_id_status_;

    float throttle_;       /* 0.0 - 1.0 */
    float nozzle_angle_;   /* -1.0 to 1.0 */
    bool reverse_;
    bool enabled_;
    bool emergency_;

    MotorState state_;
    mutable std::mutex mutex_;
};

#endif /* ESC_CONTROLLER_H */
