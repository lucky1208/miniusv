/**
 * Right Brain Bridge Implementation
 */

#include "brain_bridge_r.h"
#include "protocol_r.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <cstdio>

BrainBridgeR::BrainBridgeR(const std::string &left_brain_ip, uint16_t udp_port)
    : left_brain_ip_(left_brain_ip)
    , udp_port_(udp_port)
    , udp_sock_(-1)
    , running_(false)
    , connected_(false)
    , seq_(0)
{
    memset(&latest_cmd_, 0, sizeof(latest_cmd_));
}

BrainBridgeR::~BrainBridgeR() {
    stop();
}

bool BrainBridgeR::start() {
    udp_sock_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (udp_sock_ < 0) return false;

    /* Allow broadcast */
    int broadcast = 1;
    setsockopt(udp_sock_, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));

    /* Set receive timeout */
    struct timeval tv = {0, 20000};  /* 20ms */
    setsockopt(udp_sock_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    /* Bind to receive */
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(udp_port_);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(udp_sock_, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(udp_sock_);
        return false;
    }

    running_ = true;
    rx_thread_ = std::thread(&BrainBridgeR::receiveLoop, this);
    hb_thread_ = std::thread(&BrainBridgeR::heartbeatLoop, this);

    printf("[BrainBridgeR] Started - Left Brain at %s:%u\n",
           left_brain_ip_.c_str(), udp_port_);
    return true;
}

void BrainBridgeR::stop() {
    running_ = false;
    if (rx_thread_.joinable()) rx_thread_.join();
    if (hb_thread_.joinable()) hb_thread_.join();
    if (udp_sock_ >= 0) {
        close(udp_sock_);
        udp_sock_ = -1;
    }
}

ControlCommand BrainBridgeR::getCommand() const {
    std::lock_guard<std::mutex> lock(cmd_mutex_);
    return latest_cmd_;
}

void BrainBridgeR::receiveLoop() {
    char buffer[4096];
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    while (running_) {
        int n = recvfrom(udp_sock_, buffer, sizeof(buffer), 0,
                         (struct sockaddr *)&sender_addr, &addr_len);
        if (n < 0) continue;

        /* Parse message */
        auto msg = usv_protocol_decode(buffer, n);
        if (!msg.valid) continue;

        if (msg.msg_type == USV_MSG_COMMAND_SPEED_HEADING) {
            std::lock_guard<std::mutex> lock(cmd_mutex_);
            latest_cmd_.speed = msg.payload.cmd_speed_heading.speed;
            latest_cmd_.heading = msg.payload.cmd_speed_heading.heading;
            latest_cmd_.yaw_rate = msg.payload.cmd_speed_heading.yaw_rate;
            latest_cmd_.mode = msg.payload.cmd_speed_heading.mode;
            last_cmd_time_ = usv_get_time_us();
            connected_ = true;
        }
        else if (msg.msg_type == USV_MSG_EMERGENCY_STOP) {
            std::lock_guard<std::mutex> lock(cmd_mutex_);
            latest_cmd_.mode = 6;  /* EMERGENCY */
            latest_cmd_.speed = 0.0f;
        }
    }
}

void BrainBridgeR::sendMotorState(const DualMotorState &state) {
    USVProtocolMsg msg;
    msg.msg_type = USV_MSG_STATE_MOTORS;
    msg.payload.motor_state.left_rpm = state.left.rpm;
    msg.payload.motor_state.right_rpm = state.right.rpm;
    msg.payload.motor_state.left_current = state.left.current_a;
    msg.payload.motor_state.right_current = state.right.current_a;
    msg.payload.motor_state.left_temp = state.left.temp_c;
    msg.payload.motor_state.right_temp = state.right.temp_c;
    msg.payload.motor_state.left_fault = state.left.fault_code;
    msg.payload.motor_state.right_fault = state.right.fault_code;

    char buffer[4096];
    int len = usv_protocol_encode(msg, buffer, sizeof(buffer));
    if (len > 0) {
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(udp_port_);
        inet_pton(AF_INET, left_brain_ip_.c_str(), &addr.sin_addr);
        sendto(udp_sock_, buffer, len, 0, (struct sockaddr *)&addr, sizeof(addr));
    }
}

void BrainBridgeR::sendBMSState(const BMSState &state) {
    USVProtocolMsg msg;
    msg.msg_type = USV_MSG_STATE_BMS;
    msg.payload.bms_state.voltage = state.pack_voltage;
    msg.payload.bms_state.current = state.pack_current;
    msg.payload.bms_state.soc = state.soc;
    msg.payload.bms_state.soh = state.soh;
    msg.payload.bms_state.max_cell_temp = state.max_cell_temp;
    msg.payload.bms_state.fault_code = state.fault_code;
    msg.payload.bms_state.remaining_range = state.remaining_range_m;

    char buffer[4096];
    int len = usv_protocol_encode(msg, buffer, sizeof(buffer));
    if (len > 0) {
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(udp_port_);
        inet_pton(AF_INET, left_brain_ip_.c_str(), &addr.sin_addr);
        sendto(udp_sock_, buffer, len, 0, (struct sockaddr *)&addr, sizeof(addr));
    }
}

void BrainBridgeR::sendSensorState(const GPSData &gps, const INSData &ins) {
    USVProtocolMsg msg;
    msg.msg_type = USV_MSG_STATE_SENSORS;
    msg.payload.sensor_state.gps_lat = gps.lat;
    msg.payload.sensor_state.gps_lon = gps.lon;
    msg.payload.sensor_state.gps_alt = gps.alt;
    msg.payload.sensor_state.gps_accuracy = gps.accuracy;
    msg.payload.sensor_state.ins_roll = ins.attitude.roll;
    msg.payload.sensor_state.ins_pitch = ins.attitude.pitch;
    msg.payload.sensor_state.ins_yaw = ins.attitude.yaw;
    msg.payload.sensor_state.ins_wx = ins.angular_rate.x;
    msg.payload.sensor_state.ins_wy = ins.angular_rate.y;
    msg.payload.sensor_state.ins_wz = ins.angular_rate.z;

    char buffer[4096];
    int len = usv_protocol_encode(msg, buffer, sizeof(buffer));
    if (len > 0) {
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(udp_port_);
        inet_pton(AF_INET, left_brain_ip_.c_str(), &addr.sin_addr);
        sendto(udp_sock_, buffer, len, 0, (struct sockaddr *)&addr, sizeof(addr));
    }
}

void BrainBridgeR::heartbeatLoop() {
    while (running_) {
        /* Check for command timeout */
        uint64_t now = usv_get_time_us();
        uint64_t last = last_cmd_time_.load();
        if (now - last > 1000000) {  /* 1 second timeout */
            connected_ = false;
        }

        /* Send heartbeat */
        USVProtocolMsg msg;
        msg.msg_type = USV_MSG_HEARTBEAT;
        msg.payload.heartbeat.source = 1;  /* right_brain */

        char buffer[4096];
        int len = usv_protocol_encode(msg, buffer, sizeof(buffer));
        if (len > 0) {
            struct sockaddr_in addr;
            memset(&addr, 0, sizeof(addr));
            addr.sin_family = AF_INET;
            addr.sin_port = htons(udp_port_);
            inet_pton(AF_INET, left_brain_ip_.c_str(), &addr.sin_addr);
            sendto(udp_sock_, buffer, len, 0, (struct sockaddr *)&addr, sizeof(addr));
        }

        usleep(500000);  /* 500ms heartbeat interval */
    }
}

bool BrainBridgeR::isConnected() const {
    return connected_;
}
