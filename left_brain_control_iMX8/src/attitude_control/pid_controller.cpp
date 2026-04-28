#include "pid_controller.h"
#include <cmath>
#include <algorithm>

PIDController::PIDController(float kp, float ki, float kd,
                             float output_min, float output_max,
                             float integral_limit)
    : kp_(kp), ki_(ki), kd_(kd)
    , output_min_(output_min), output_max_(output_max)
    , integral_limit_(integral_limit)
    , integral_(0.0f), prev_error_(0.0f), first_(true)
{
}

float PIDController::update(float setpoint, float measurement, float dt) {
    float error = setpoint - measurement;

    /* Proportional */
    float p_out = kp_ * error;

    /* Integral with anti-windup */
    integral_ += error * dt;
    if (integral_limit_ > 0.0f) {
        integral_ = std::clamp(integral_, -integral_limit_, integral_limit_);
    }
    float i_out = ki_ * integral_;

    /* Derivative (on error, filtered) */
    float d_out = 0.0f;
    if (!first_ && dt > 0.0f) {
        float derivative = (error - prev_error_) / dt;
        d_out = kd_ * derivative;
    }
    prev_error_ = error;
    first_ = false;

    /* Total output with clamping */
    float output = p_out + i_out + d_out;
    return std::clamp(output, output_min_, output_max_);
}

void PIDController::reset() {
    integral_ = 0.0f;
    prev_error_ = 0.0f;
    first_ = true;
}

void PIDController::setGains(float kp, float ki, float kd) {
    kp_ = kp;
    ki_ = ki;
    kd_ = kd;
}
