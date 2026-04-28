/**
 * Jet Thrust Mapper
 *
 * Maps high-level (speed, heading) commands to individual
 * jet thrust and nozzle angle for dual Marine Jet propulsion.
 *
 * Dual jet propulsion allows:
 * - Differential thrust for turning
 * - Nozzle vectoring for fine heading control
 * -原地转向 (pivot turn) via opposite thrust
 * - Quick reverse via bucket deflectors
 */

#ifndef JET_THRUST_MAPPER_H
#define JET_THRUST_MAPPER_H

#include "../../include/usv_control/usv_types.h"

class JetThrustMapper {
public:
    JetThrustMapper();

    /**
     * Map speed + yaw_rate to dual jet thrust commands
     *
     * @param speed     Target speed (m/s, positive=forward)
     * @param yaw_rate  Target yaw rate (rad/s, positive=CCW)
     * @param current_speed  Current speed for feedforward
     * @return JetThrustCommand for left and right jets
     */
    JetThrustCommand mapSpeedHeading(float speed, float yaw_rate,
                                      float current_speed);

    /**
     * Emergency stop - zero thrust, neutral nozzle
     */
    JetThrustCommand emergencyStop();

    /* Configuration */
    void setMaxThrust(float max_thrust);     /* 0-1 */
    void setTurnGain(float gain);
    void setNozzleGain(float gain);

private:
    float max_thrust_;     /* Maximum thrust fraction (0-1) */
    float turn_gain_;      /* Differential thrust gain for turning */
    float nozzle_gain_;    /* Nozzle angle gain for heading */
    float max_speed_;      /* Max speed (m/s) for normalization */
};

#endif /* JET_THRUST_MAPPER_H */
