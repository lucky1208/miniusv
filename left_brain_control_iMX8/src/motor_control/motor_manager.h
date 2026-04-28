/**
 * Motor Manager - Orchestrates dual ESC + Jet Thrust Mapper
 */

#ifndef MOTOR_MANAGER_H
#define MOTOR_MANAGER_H

#include "esc_controller.h"
#include "jet_thrust_mapper.h"
#include "../../include/usv_control/usv_types.h"

class MotorManager {
public:
    MotorManager(CANInterface *can);

    /* Set control command from Left Brain */
    void setCommand(const ControlCommand &cmd);

    /* Execute control loop (called at 50Hz) */
    void update(float dt);

    /* Get dual motor state */
    DualMotorState getState() const;

    /* Emergency stop */
    void emergencyStop();

    /* Enable/disable */
    void setEnabled(bool enabled);

private:
    ESCController left_esc_;
    ESCController right_esc_;
    JetThrustMapper thrust_mapper_;

    ControlCommand command_;
    DualMotorState state_;
    bool enabled_;
    float current_speed_;

    /* PID for speed control */
    float speed_kp_, speed_ki_, speed_kd_;
    float speed_integral_;
    float speed_prev_error_;
};

#endif /* MOTOR_MANAGER_H */
