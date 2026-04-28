cmake_minimum_required(VERSION 3.10)
project(usv_left_brain_control C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags for i.MX8 (ARM Cortex-A53)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -O2 -march=armv8-a")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O2 -march=armv8-a")

# Find required libraries
find_package(Threads REQUIRED)

# SocketCAN is available on Linux, no extra package needed
# For real-time: link with -lrt for POSIX real-time extensions

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/include/usv_control
)

# CAN Bus library
add_library(usv_can_bus STATIC
    src/can_bus/can_interface.c
    src/can_bus/can_protocol.c
)
target_link_libraries(usv_can_bus Threads::Threads rt)

# Motor Control library
add_library(usv_motor_control STATIC
    src/motor_control/esc_controller.cpp
    src/motor_control/jet_thrust_mapper.cpp
    src/motor_control/motor_manager.cpp
)
target_link_libraries(usv_motor_control usv_can_bus Threads::Threads)

# BMS Monitor library
add_library(usv_bms STATIC
    src/bms_monitor/bms_monitor.cpp
    src/bms_monitor/power_manager.cpp
)
target_link_libraries(usv_bms usv_can_bus Threads::Threads)

# Navigation Sensors library
add_library(usv_nav_sensors STATIC
    src/navigation_sensors/gps_receiver.cpp
    src/navigation_sensors/ins_reader.cpp
    src/navigation_sensors/sensor_manager.cpp
)
target_link_libraries(usv_nav_sensors usv_can_bus Threads::Threads rt)

# Attitude Control library (PID + LQR)
add_library(usv_attitude_control STATIC
    src/attitude_control/pid_controller.cpp
    src/attitude_control/heading_controller.cpp
    src/attitude_control/speed_controller.cpp
)

# Brain Bridge (communication with Right Brain AI)
add_library(usv_brain_bridge_r STATIC
    src/brain_bridge/brain_bridge_r.cpp
    src/brain_bridge/protocol_r.cpp
)
target_link_libraries(usv_brain_bridge_r Threads::Threads rt)

# Watchdog
add_library(usv_watchdog STATIC
    src/watchdog/watchdog.cpp
)
target_link_libraries(usv_watchdog Threads::Threads rt)

# Main executable
add_executable(left_brain_control_main
    src/main.cpp
)
target_link_libraries(left_brain_control_main
    usv_can_bus
    usv_motor_control
    usv_bms
    usv_nav_sensors
    usv_attitude_control
    usv_brain_bridge_r
    usv_watchdog
    Threads::Threads
    rt
    m
)

# Install
install(TARGETS left_brain_control_main
        RUNTIME DESTINATION bin)
install(TARGETS
    usv_can_bus usv_motor_control usv_bms
    usv_nav_sensors usv_attitude_control
    usv_brain_bridge_r usv_watchdog
    ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY config/ DESTINATION etc/usv)
