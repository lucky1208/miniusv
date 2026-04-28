#include "heading_controller.h"
#include <cmath>

HeadingController::HeadingController()
    : pid_(2.0f, 0.1f, 0.5f, -0.5f, 0.5f, 1.0f)  /* yaw rate limits: ±0.5 rad/s */
{
}

float HeadingController::compute(float target_heading, float current_heading, float dt) {
    /* Wrap heading error to [-π, π] */
    float error = wrapAngle(target_heading - current_heading);
    return pid_.update(0.0f, -error, dt);  /* PID on error, output = yaw_rate */
}

void HeadingController::setGains(float kp, float ki, float kd) {
    pid_.setGains(kp, ki, kd);
}

float HeadingController::wrapAngle(float angle) {
    while (angle > M_PI) angle -= 2.0f * M_PI;
    while (angle < -M_PI) angle += 2.0f * M_PI;
    return angle;
}
