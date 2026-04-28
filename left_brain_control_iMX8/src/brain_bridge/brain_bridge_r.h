/**
 * Right Brain Bridge - Communication with Left Brain (Jetson Orin NX)
 *
 * Receives control commands and sends status via UDP.
 */

#ifndef BRAIN_BRIDGE_R_H
#define BRAIN_BRIDGE_R_H

#include <cstdint>
#include <string>
#include <thread>
#include <mutex>
#include <atomic>
#include "../../include/usv_control/usv_types.h"

class BrainBridgeR {
public:
    BrainBridgeR(const std::string &left_brain_ip = "192.168.1.1",
                 uint16_t udp_port = 9876);

    ~BrainBridgeR();

    bool start();
    void stop();

    /* Get latest command from Left Brain */
    ControlCommand getCommand() const;

    /* Send status to Left Brain */
    void sendMotorState(const DualMotorState &state);
    void sendBMSState(const BMSState &state);
    void sendSensorState(const GPSData &gps, const INSData &ins);

    /* Connection status */
    bool isConnected() const;

private:
    void receiveLoop();
    void sendLoop();
    void heartbeatLoop();

    std::string left_brain_ip_;
    uint16_t udp_port_;
    int udp_sock_;

    std::atomic<bool> running_;
    std::thread rx_thread_;
    std::thread hb_thread_;

    ControlCommand latest_cmd_;
    mutable std::mutex cmd_mutex_;

    std::atomic<uint64_t> last_cmd_time_;
    std::atomic<bool> connected_;
    std::atomic<uint32_t> seq_;
};

#endif
