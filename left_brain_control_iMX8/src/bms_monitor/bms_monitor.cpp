/**
 * BMS Monitor Implementation
 */

#include "bms_monitor.h"
#include <cstring>
#include <cmath>

BMSMonitor::BMSMonitor(CANInterface *can)
    : can_(can)
{
    memset(&state_, 0, sizeof(state_));
    state_.soh = 100.0f;
}

void BMSMonitor::updateStatus(const CANFrame *frame) {
    if (frame->can_id != CAN_ID_BMS_STATUS) return;

    std::lock_guard<std::mutex> lock(mutex_);

    BMSStatusFrame bms;
    bms_status_from_bytes(frame->data, &bms);

    state_.pack_voltage = static_cast<float>(bms.voltage_01v) * 0.1f;
    state_.pack_current = static_cast<float>(bms.current_01a) * 0.1f;
    state_.soc = static_cast<float>(bms.soc_pct);
    state_.soh = static_cast<float>(bms.soh_pct);
    state_.max_cell_temp = static_cast<float>(bms.max_cell_temp_c) - 40.0f;
    state_.fault_code = bms.fault_code;
    state_.charging = (state_.pack_current < 0.0f);

    /* Estimate remaining range (rough) */
    /* At 15 knots (7.7 m/s) ~15kW, range = SOC% * 50km */
    float speed_economy = 7.7f;  /* m/s at 15 knots */
    float power_economy = 15000.0f;  /* W at 15 knots */
    float energy_remaining = (state_.soc / 100.0f) * 59850.0f;  /* Wh */
    float time_remaining_h = energy_remaining / (power_economy / 1000.0f);
    state_.remaining_range_m = time_remaining_h * speed_economy * 3600.0f;
}

BMSState BMSMonitor::getState() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return state_;
}

bool BMSMonitor::isSafe() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return state_.fault_code == 0
        && state_.soc > 5.0f
        && state_.max_cell_temp < 55.0f
        && state_.min_cell_voltage > 2.5f;
}

float BMSMonitor::getMaxDischargeCurrent() const {
    std::lock_guard<std::mutex> lock(mutex_);
    /* Reduce max current at low SOC or high temperature */
    float current_limit = 600.0f;  /* 2C for 300Ah pack */

    if (state_.soc < 20.0f) {
        current_limit *= (state_.soc / 20.0f);
    }
    if (state_.max_cell_temp > 45.0f) {
        current_limit *= (1.0f - (state_.max_cell_temp - 45.0f) / 15.0f);
    }

    return std::fmax(current_limit, 50.0f);  /* Minimum 50A */
}

float BMSMonitor::getRemainingTime() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (state_.pack_current <= 0.0f) return -1.0f;  /* Charging or idle */
    float energy_remaining = (state_.soc / 100.0f) * 59850.0f;  /* Wh */
    float power = state_.pack_voltage * state_.pack_current / 1000.0f;  /* kW */
    if (power < 0.1f) return 3600.0f;  /* Very low power */
    return (energy_remaining / power) * 3600.0f;  /* seconds */
}
