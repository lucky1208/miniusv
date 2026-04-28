#include "speed_controller.h"

SpeedController::SpeedController()
    : pid_(0.5f, 0.1f, 0.05f, -1.0f, 1.0f, 5.0f)
{
}

float SpeedController::compute(float target_speed, float current_speed, float dt) {
    return pid_.update(target_speed, current_speed, dt);
}

void SpeedController::setGains(float kp, float ki, float kd) {
    pid_.setGains(kp, ki, kd);
}
