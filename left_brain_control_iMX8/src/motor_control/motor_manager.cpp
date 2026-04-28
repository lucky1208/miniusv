/**
 * Motor Manager Implementation
 */

#include "motor_manager.h"
#include <cmath>
#include <algorithm>
#include <cstring>

MotorManager::MotorManager(CANInterface *can)
    : left_esc_(can, CAN_ID_ESC_LEFT_TX, CAN_ID_ESC_LEFT_RX)
    , right_esc_(can, CAN_ID_ESC_RIGHT_TX, CAN_ID_ESC_RIGHT_RX)
    , enabled_(false)
    , current_speed_(0.0f)
    , speed_kp_(0.5f)
    , speed_ki_(0.1f)
    , speed_kd_(0.05f)
    , speed_integral_(0.0f)
    , speed_prev_error_(0.0f)
{
    memset(&command_, 0, sizeof(command_));
    memset(&state_, 0, sizeof(state_));
}

void MotorManager::setCommand(const ControlCommand &cmd) {
    command_ = cmd;
}

void MotorManager::update(float dt) {
    if (!enabled_) {
        left_esc_.setThrottle(0.0f);
        right_esc_.setThrottle(0.0f);
        left_esc_.sendCommand();
        right_esc_.sendCommand();
        return;
    }

    /* Emergency mode */
    if (command_.mode == 6) {  /* MODE_EMERGENCY */
        emergencyStop();
        return;
    }

    /* Speed PID control */
    float speed_error = command_.speed - current_speed_;
    speed_integral_ += speed_error * dt;
    speed_integral_ = std::clamp(speed_integral_, -5.0f, 5.0f);  /* anti-windup */
    float speed_derivative = (speed_error - speed_prev_error_) / dt;
    speed_prev_error_ = speed_error;

    float speed_output = speed_kp_ * speed_error
                       + speed_ki_ * speed_integral_
                       + speed_kd_ * speed_derivative;

    /* Map to jet thrust */
    JetThrustCommand jet_cmd = thrust_mapper_.mapSpeedHeading(
        speed_output, command_.yaw_rate, current_speed_
    );

    /* Apply to ESCs */
    left_esc_.setThrottle(std::fabs(jet_cmd.left_thrust));
    left_esc_.setNozzleAngle(jet_cmd.left_nozzle);
    left_esc_.setReverse(jet_cmd.left_thrust < 0.0f);

    right_esc_.setThrottle(std::fabs(jet_cmd.right_thrust));
    right_esc_.setNozzleAngle(jet_cmd.right_nozzle);
    right_esc_.setReverse(jet_cmd.right_thrust < 0.0f);

    /* Send CAN commands */
    left_esc_.sendCommand();
    right_esc_.sendCommand();

    /* Update state */
    state_.left = left_esc_.getState();
    state_.right = right_esc_.getState();
}

DualMotorState MotorManager::getState() const {
    return state_;
}

void MotorManager::emergencyStop() {
    left_esc_.emergencyStop();
    right_esc_.emergencyStop();
    left_esc_.sendCommand();
    right_esc_.sendCommand();
    memset(&command_, 0, sizeof(command_));
}

void MotorManager::setEnabled(bool enabled) {
    enabled_ = enabled;
    left_esc_.setEnabled(enabled);
    right_esc_.setEnabled(enabled);
}
