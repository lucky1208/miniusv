#include "power_manager.h"
#include <cmath>

PowerManager::PowerManager(BMSMonitor *bms) : bms_(bms) {}

bool PowerManager::canProvidePower(float requested_watts) const {
    if (!bms_->isSafe()) return false;
    auto state = bms_->getState();
    float max_current = bms_->getMaxDischargeCurrent();
    float max_power = state.pack_voltage * max_current;
    return requested_watts <= max_power;
}

float PowerManager::getCurrentPower() const {
    auto state = bms_->getState();
    return std::fabs(state.pack_voltage * state.pack_current);
}

bool PowerManager::isVoltageOK() const {
    auto state = bms_->getState();
    return state.pack_voltage > 180.0f && state.pack_voltage < 230.0f;
}
