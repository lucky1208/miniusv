/**
 * Heading Controller - PID heading control for USV
 */

#ifndef HEADING_CONTROLLER_H
#define HEADING_CONTROLLER_H

#include "pid_controller.h"

class HeadingController {
public:
    HeadingController();

    /* Compute yaw rate command to reach target heading */
    float compute(float target_heading, float current_heading, float dt);

    void setGains(float kp, float ki, float kd);

private:
    PIDController pid_;
    static float wrapAngle(float angle);
};

#endif
