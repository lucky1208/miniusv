#!/usr/bin/env python3
"""USV Right Brain (AI) Main Node - ROS2 Application

Main entry point for the Right Brain (AI) on Jetson Orin NX.
Responsible for AI perception, planning, and decision-making.
Sends control commands to Left Brain (Control) via Brain Bridge.

Architecture:
┌─────────────────────────────────────────────────┐
│         Right Brain (AI) - Jetson Orin NX        │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │Perception │  │   ATR    │  │   Planning   │  │
│  │LiDAR+Radar│→│ YOLOv8   │→│  A* + RRT*   │  │
│  │+Camera    │  │+Tracker  │  │  + Waypoints │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│         │             │              │           │
│  ┌──────────┐  ┌──────────┐         │           │
│  │SensorFusion│ │ Threat  │←────────┘           │
│  │  EKF      │  │Assess   │                     │
│  └──────────┘  └──────────┘                     │
│         │             │                          │
│  ┌──────────────────────────────────────────┐   │
│  │           Avoidance (DWA + COLREGs)      │   │
│  └──────────────────────────────────────────┘   │
│                        │                         │
│  ┌──────────────────────────────────────────┐   │
│  │     Brain Bridge → Left Brain (Control)  │   │
│  │   (speed, heading commands via UDP)      │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import numpy as np
import time
import signal
import sys

# Import our modules
from usv_perception import (
    LidarProcessor, RadarProcessor, CameraProcessor,
    SensorFusionEKF, OccupancyMapBuilder
)
from usv_atr import ATRPipeline
from usv_planning import (
    AStarPlanner, RRTStarPlanner, WaypointManager, MissionStateMachine, MissionState
)
from usv_avoidance import DWAAvoidance, PotentialFieldAvoidance, COLREGsCompliance
from usv_threat_assessment import ThreatEvaluator
from usv_brain_bridge import BrainBridge, MessageType


class RightBrainAINode(Node):
    """Main Right Brain (AI) ROS2 Node

    Orchestrates all perception, planning, and decision modules.
    Sends control commands to Left Brain (Control) via BrainBridge.
    """

    def __init__(self):
        super().__init__('usv_right_brain_ai')

        # Declare parameters
        self.declare_parameter('right_brain_ip', '192.168.1.100')
        self.declare_parameter('control_rate_hz', 20.0)
        self.declare_parameter('perception_rate_hz', 10.0)
        self.declare_parameter('planning_rate_hz', 2.0)

        # Initialize modules
        self.get_logger().info('Initializing Right Brain (AI) modules...')

        # Perception
        self.lidar = LidarProcessor()
        self.radar = RadarProcessor()
        self.camera = CameraProcessor()
        self.sensor_fusion = SensorFusionEKF()
        self.occupancy_map = OccupancyMapBuilder()

        # ATR
        self.atr = ATRPipeline()
        atr_ok = self.atr.initialize()
        self.get_logger().info(f'ATR initialized: {atr_ok}')

        # Planning
        self.a_star = AStarPlanner()
        self.rrt_star = RRTStarPlanner()
        self.waypoint_mgr = WaypointManager()
        self.mission_sm = MissionStateMachine()

        # Avoidance
        self.dwa = DWAAvoidance()
        self.pot_field = PotentialFieldAvoidance()
        self.colregs = COLREGsCompliance()

        # Threat Assessment
        self.threat_eval = ThreatEvaluator()

        # Brain Bridge
        right_ip = self.get_parameter('right_brain_ip').value
        self.bridge = BrainBridge(right_brain_ip=right_ip)
        bridge_ok = self.bridge.start()
        self.get_logger().info(f'Brain Bridge started: {bridge_ok}')

        # State
        self._current_path = []
        self._last_control_time = 0.0
        self._last_perception_time = 0.0
        self._last_planning_time = 0.0
        self._frame_count = 0

        # Control loop timer
        control_rate = self.get_parameter('control_rate_hz').value
        self._control_timer = self.create_timer(
            1.0 / control_rate, self._control_loop
        )

        # Perception loop timer
        perception_rate = self.get_parameter('perception_rate_hz').value
        self._perception_timer = self.create_timer(
            1.0 / perception_rate, self._perception_loop
        )

        # Planning loop timer
        planning_rate = self.get_parameter('planning_rate_hz').value
        self._planning_timer = self.create_timer(
            1.0 / planning_rate, self._planning_loop
        )

        self.get_logger().info('Right Brain (AI) initialized and running!')

    def _perception_loop(self):
        """Perception processing loop (10Hz)

        Processes sensor data, runs ATR, updates occupancy map.
        """
        try:
            # Get camera frames
            visible, ir = self.camera.get_frames()

            # Run ATR on camera
            if visible is not None:
                tracked_targets = self.atr.process_dual(visible, ir)
            else:
                tracked_targets = []

            # Update sensor fusion with Right Brain sensor data
            if self.bridge.sensor_state:
                ss = self.bridge.sensor_state
                self.sensor_fusion.update_gps(ss.gps_lat, ss.gps_lon, ss.gps_alt)
                self.sensor_fusion.update_ins(
                    ss.ins_roll, ss.ins_pitch, ss.ins_yaw,
                    ss.ins_wx, ss.ins_wy, ss.ins_wz
                )

            # Get fused state
            state = self.sensor_fusion.get_state()

            # Update threat evaluator with USV state
            self.threat_eval.update_usv_state(
                state.x, state.y, state.vx, state.vy
            )

            # Evaluate threats
            target_dicts = self.atr.tracker.get_tracks_dict()
            threats = self.threat_eval.evaluate_all(target_dicts)

            # Check for emergency threats
            for threat in threats:
                if threat.threat_level >= 4:  # CRITICAL or IMMINENT
                    if self.mission_sm.state != MissionState.EMERGENCY:
                        self.mission_sm.transition(
                            MissionState.AVOIDING,
                            reason=f"Threat: {threat.target_type} at {threat.distance}m"
                        )

            self._frame_count += 1

        except Exception as e:
            self.get_logger().error(f'Perception loop error: {e}')

    def _planning_loop(self):
        """Path planning loop (2Hz)

        Runs A* global planning and RRT* local replanning.
        """
        try:
            state = self.sensor_fusion.get_state()

            # Check waypoint arrival
            self.waypoint_mgr.check_arrival(state.x, state.y)

            # Get current waypoint
            wp = self.waypoint_mgr.get_current_waypoint()
            if wp is None:
                return

            # Get occupancy grid for planning
            grid = self.occupancy_map.get_grid_for_planning()

            # Global planning (A*)
            start = (int(state.x), int(state.y))
            goal = (int(wp.x), int(wp.y))

            path = self.a_star.plan(grid, start, goal)
            if path:
                # Smooth path
                self._current_path = self.a_star.smooth_path(
                    [(p[0] * 0.5, p[1] * 0.5) for p in path]  # grid to world
                )

        except Exception as e:
            self.get_logger().error(f'Planning loop error: {e}')

    def _control_loop(self):
        """Main control loop (20Hz)

        Computes avoidance maneuver and sends commands to Right Brain.
        """
        try:
            state = self.sensor_fusion.get_state()

            # Get current waypoint
            wp = self.waypoint_mgr.get_current_waypoint()
            if wp is None:
                # No mission - idle
                self.bridge.send_speed_heading(0.0, state.yaw, mode="idle")
                return

            # Get obstacle list from LiDAR + Radar
            obstacles = []
            for obs in self.lidar.obstacles:
                obstacles.append({
                    'x': obs.center[0], 'y': obs.center[1],
                    'vx': obs.velocity[0], 'vy': obs.velocity[1],
                })
            for track in self.radar.tracks.values():
                obstacles.append({
                    'x': track.x, 'y': track.y,
                    'vx': track.vx, 'vy': track.vy,
                })

            # Compute avoidance command using DWA
            if self.mission_sm.state == MissionState.AVOIDING or len(obstacles) > 0:
                speed, yaw_rate = self.dwa.compute_command(
                    state.x, state.y, state.yaw,
                    np.sqrt(state.vx**2 + state.vy**2), 0.0,
                    wp.x, wp.y, obstacles
                )
                heading = state.yaw + yaw_rate * 0.05  # dt = 50ms
            else:
                # Simple heading control toward waypoint
                dx = wp.x - state.x
                dy = wp.y - state.y
                desired_heading = np.arctan2(dy, dx)
                dist = np.sqrt(dx*dx + dy*dy)

                heading = desired_heading
                speed = min(wp.speed, dist * 0.5)  # Slow down near waypoint

            # Send command to Left Brain (Control)
            self.bridge.send_speed_heading(
                speed=speed,
                heading=heading,
                yaw_rate=0.0,
                mode=self.mission_sm.state.name.lower()
            )

        except Exception as e:
            self.get_logger().error(f'Control loop error: {e}')

    def destroy_node(self):
        """Clean shutdown"""
        self.camera.stop()
        self.bridge.stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = RightBrainAINode()

    # Handle SIGINT for clean shutdown
    def signal_handler(sig, frame):
        node.get_logger().info('Shutting down Right Brain (AI)...')
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
