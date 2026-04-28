/**
 * ESC Controller Implementation
 */

#include "esc_controller.h"
#include <cstring>
#include <algorithm>

ESCController::ESCController(CANInterface *can, uint32_t can_id_cmd, uint32_t can_id_status)
    : can_(can)
    , can_id_cmd_(can_id_cmd)
    , can_id_status_(can_id_status)
    , throttle_(0.0f)
    , nozzle_angle_(0.0f)
    , reverse_(false)
    , enabled_(false)
    , emergency_(false)
{
    memset(&state_, 0, sizeof(state_));
}

void ESCController::setThrottle(float throttle) {
    std::lock_guard<std::mutex> lock(mutex_);
    throttle_ = std::clamp(throttle, 0.0f, 1.0f);
}

void ESCController::setNozzleAngle(float angle) {
    std::lock_guard<std::mutex> lock(mutex_);
    nozzle_angle_ = std::clamp(angle, -1.0f, 1.0f);
}

void ESCController::setReverse(bool reverse) {
    std::lock_guard<std::mutex> lock(mutex_);
    reverse_ = reverse;
}

void ESCController::setEnabled(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    enabled_ = enabled;
}

void ESCController::emergencyStop() {
    std::lock_guard<std::mutex> lock(mutex_);
    emergency_ = true;
    throttle_ = 0.0f;
    enabled_ = false;
}

void ESCController::updateStatus(const CANFrame *frame) {
    if (frame->can_id != can_id_status_) return;

    std::lock_guard<std::mutex> lock(mutex_);

    ESCStatusFrame status;
    esc_status_from_bytes(frame->data, &status);

    state_.rpm = static_cast<float>(status.rpm);
    state_.current_a = static_cast<float>(status.current_01a) * 0.1f;
    state_.temp_c = static_cast<float>(status.temp_01c) * 0.1f - 40.0f;
    state_.fault_code = status.fault_code;
    state_.duty_cycle = throttle_;
    state_.enabled = enabled_;
}

MotorState ESCController::getState() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return state_;
}

int ESCController::sendCommand() {
    std::lock_guard<std::mutex> lock(mutex_);

    if (!can_ || !can_->is_open) return -1;

    ESCCommandFrame cmd;
    memset(&cmd, 0, sizeof(cmd));

    if (emergency_ || !enabled_) {
        cmd.throttle = 0;
        cmd.mode = 0;  /* disabled */
    } else {
        /* Map throttle 0.0-1.0 to 0-65535 */
        cmd.throttle = static_cast<uint16_t>(throttle_ * 65535.0f);
        cmd.mode = 1;  /* speed mode */

        /* Map nozzle -1.0 to 1.0 to -32768 to 32767 */
        cmd.nozzle = static_cast<int16_t>(nozzle_angle_ * 32767.0f);
    }

    cmd.direction = reverse_ ? 1 : 0;

    CANFrame frame;
    frame.can_id = can_id_cmd_;
    frame.dlc = 8;
    esc_cmd_to_bytes(&cmd, frame.data);

    return can_send(can_, &frame);
}
