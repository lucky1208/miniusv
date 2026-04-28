/**
 * PID Controller for USV Attitude Control
 */

#ifndef PID_CONTROLLER_H
#define PID_CONTROLLER_H

class PIDController {
public:
    PIDController(float kp, float ki, float kd,
                  float output_min, float output_max,
                  float integral_limit = 0.0f);

    float update(float setpoint, float measurement, float dt);
    void reset();
    void setGains(float kp, float ki, float kd);

private:
    float kp_, ki_, kd_;
    float output_min_, output_max_;
    float integral_limit_;
    float integral_;
    float prev_error_;
    bool first_;
};

#endif
