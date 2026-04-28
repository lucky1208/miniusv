#ifndef SPEED_CONTROLLER_H
#define SPEED_CONTROLLER_H

#include "pid_controller.h"

class SpeedController {
public:
    SpeedController();
    float compute(float target_speed, float current_speed, float dt);
    void setGains(float kp, float ki, float kd);
private:
    PIDController pid_;
};

#endif
