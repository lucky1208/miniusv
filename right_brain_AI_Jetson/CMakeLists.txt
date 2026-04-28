cmake_minimum_required(VERSION 3.8)
project(usv_right_brain_ai)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

# Install Python modules
ament_python_install_package(usv_perception)
ament_python_install_package(usv_atr)
ament_python_install_package(usv_planning)
ament_python_install_package(usv_avoidance)
ament_python_install_package(usv_brain_bridge)
ament_python_install_package(usv_threat_assessment)

# Install config files
install(DIRECTORY config/ DESTINATION share/${PROJECT_NAME}/config)
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)
install(DIRECTORY models/ DESTINATION share/${PROJECT_NAME}/models)
install(DIRECTORY scripts/ DESTINATION share/${PROJECT_NAME}/scripts
        USE_SOURCE_PERMISSIONS)

ament_package()
