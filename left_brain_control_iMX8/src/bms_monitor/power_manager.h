/**
 * Power Manager - Manages DC/DC converters and power distribution
 */

#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include "bms_monitor.h"

class PowerManager {
public:
    PowerManager(BMSMonitor *bms);

    /* Check if system can operate at requested power level */
    bool canProvidePower(float requested_watts) const;

    /* Get current power consumption */
    float getCurrentPower() const;

    /* Get system voltage status */
    bool isVoltageOK() const;

private:
    BMSMonitor *bms_;
};

#endif
