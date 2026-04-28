/**
 * Jet Thrust Mapper Implementation
 */

#include "jet_thrust_mapper.h"
#include <cmath>
#include <algorithm>

JetThrustMapper::JetThrustMapper()
    : max_thrust_(0.95f)
    , turn_gain_(0.5f)
    , nozzle_gain_(0.8f)
    , max_speed_(23.0f)  /* ~45 knots */
{
}

JetThrustCommand JetThrustMapper::mapSpeedHeading(
    float speed, float yaw_rate, float current_speed)
{
    JetThrustCommand cmd = {0};

    /* Normalize speed to thrust fraction */
    float base_thrust = std::fabs(speed) / max_speed_;
    base_thrust = std::clamp(base_thrust, 0.0f, max_thrust_);

    /* Direction */
    bool forward = (speed >= 0.0f);

    /* Differential thrust for turning
     * yaw_rate > 0 (turn left/CCW): left less, right more
     * yaw_rate < 0 (turn right/CW): left more, right less
     */
    float diff_thrust = yaw_rate * turn_gain_;
    diff_thrust = std::clamp(diff_thrust, -0.5f, 0.5f);

    float left_thrust = base_thrust - diff_thrust;
    float right_thrust = base_thrust + diff_thrust;

    /* Clamp to limits */
    left_thrust = std::clamp(left_thrust, -max_thrust_, max_thrust_);
    right_thrust = std::clamp(right_thrust, -max_thrust_, max_thrust_);

    /* Nozzle angle for fine heading control
     * Nozzle deflects jet stream for additional turning moment
     */
    float nozzle = yaw_rate * nozzle_gain_;
    nozzle = std::clamp(nozzle, -1.0f, 1.0f);

    /* Apply direction */
    if (!forward) {
        left_thrust = -left_thrust;
        right_thrust = -right_thrust;
    }

    cmd.left_thrust = left_thrust;
    cmd.right_thrust = right_thrust;
    cmd.left_nozzle = -nozzle;   /* Left nozzle opposite for coordinated turn */
    cmd.right_nozzle = nozzle;

    return cmd;
}

JetThrustCommand JetThrustMapper::emergencyStop() {
    return {0.0f, 0.0f, 0.0f, 0.0f};
}

void JetThrustMapper::setMaxThrust(float max_thrust) {
    max_thrust_ = std::clamp(max_thrust, 0.0f, 1.0f);
}

void JetThrustMapper::setTurnGain(float gain) {
    turn_gain_ = gain;
}

void JetThrustMapper::setNozzleGain(float gain) {
    nozzle_gain_ = gain;
}
