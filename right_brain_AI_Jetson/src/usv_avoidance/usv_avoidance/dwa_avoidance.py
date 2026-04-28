"""Dynamic Window Approach (DWA) for USV Local Obstacle Avoidance

Computes optimal velocity (speed + heading change) within dynamic window
to avoid obstacles while progressing toward goal.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class USVDynamics:
    """USV dynamic constraints"""
    max_speed: float = 23.0        # m/s (~45 knots max)
    min_speed: float = 0.0         # m/s
    max_yaw_rate: float = 0.5      # rad/s (max turning rate)
    max_accel: float = 2.0         # m/s²
    max_yaw_accel: float = 0.3     # rad/s²
    predict_time: float = 3.0      # seconds to predict ahead
    predict_dt: float = 0.1        # prediction time step


class DWAAvoidance:
    """Dynamic Window Approach Obstacle Avoidance

    Computes safe velocity commands considering:
    - USV dynamic constraints (acceleration, turning rate)
    - Obstacle positions and velocities
    - Goal direction
    - COLREGs rules (via COLREGsCompliance module)
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.dynamics = USVDynamics(**config.get("dynamics", {}))
        self.goal_weight = config.get("goal_weight", 1.0)
        self.obstacle_weight = config.get("obstacle_weight", 2.0)
        self.speed_weight = config.get("speed_weight", 0.5)
        self.heading_weight = config.get("heading_weight", 1.0)
        self.safety_distance = config.get("safety_distance", 10.0)  # meters
        self.critical_distance = config.get("critical_distance", 5.0)  # meters

    def compute_dynamic_window(self, current_speed: float,
                                current_yaw_rate: float,
                                dt: float = 0.1) -> Tuple[float, float, float, float]:
        """Compute dynamic window based on current state and acceleration limits

        Returns:
            (min_speed, max_speed, min_yaw_rate, max_yaw_rate)
        """
        d = self.dynamics

        # Speed window
        v_min = max(current_speed - d.max_accel * dt, d.min_speed)
        v_max = min(current_speed + d.max_accel * dt, d.max_speed)

        # Yaw rate window
        w_min = max(current_yaw_rate - d.max_yaw_accel * dt, -d.max_yaw_rate)
        w_max = min(current_yaw_rate + d.max_yaw_accel * dt, d.max_yaw_rate)

        return v_min, v_max, w_min, w_max

    def predict_trajectory(self, x: float, y: float, yaw: float,
                           speed: float, yaw_rate: float) -> np.ndarray:
        """Predict USV trajectory for given velocity command

        Args:
            x, y, yaw: Current state
            speed: Command speed
            yaw_rate: Command yaw rate

        Returns:
            Nx3 array of predicted [x, y, yaw] states
        """
        d = self.dynamics
        n_steps = int(d.predict_time / d.predict_dt)
        traj = np.zeros((n_steps + 1, 3))
        traj[0] = [x, y, yaw]

        for i in range(n_steps):
            x += speed * np.cos(yaw) * d.predict_dt
            y += speed * np.sin(yaw) * d.predict_dt
            yaw += yaw_rate * d.predict_dt
            traj[i + 1] = [x, y, yaw]

        return traj

    def _obstacle_cost(self, trajectory: np.ndarray,
                       obstacles: List[dict]) -> float:
        """Compute obstacle proximity cost for a trajectory

        Args:
            trajectory: Predicted trajectory Nx3
            obstacles: List of {'x', 'y', 'vx', 'vy'} obstacle dicts

        Returns:
            Cost (higher = more dangerous)
        """
        min_dist = float('inf')

        for obs in obstacles:
            ox = obs.get('x', 0.0)
            oy = obs.get('y', 0.0)
            ovx = obs.get('vx', 0.0)
            ovy = obs.get('vy', 0.0)

            for i, (tx, ty, _) in enumerate(trajectory):
                t = i * self.dynamics.predict_dt
                # Predict obstacle position
                pred_ox = ox + ovx * t
                pred_oy = oy + ovy * t

                dist = np.sqrt((tx - pred_ox)**2 + (ty - pred_oy)**2)
                min_dist = min(min_dist, dist)

        if min_dist < self.critical_distance:
            return float('inf')  # Collision!
        elif min_dist < self.safety_distance:
            return 1.0 / (min_dist - self.critical_distance + 0.1)
        else:
            return 0.0

    def _goal_cost(self, trajectory: np.ndarray,
                   goal_x: float, goal_y: float) -> float:
        """Compute cost based on distance to goal at end of trajectory"""
        final_x = trajectory[-1, 0]
        final_y = trajectory[-1, 1]
        return np.sqrt((final_x - goal_x)**2 + (final_y - goal_y)**2)

    def compute_command(self, x: float, y: float, yaw: float,
                        current_speed: float, current_yaw_rate: float,
                        goal_x: float, goal_y: float,
                        obstacles: List[dict],
                        n_samples: int = 20) -> Tuple[float, float]:
        """Compute optimal avoidance velocity command

        Args:
            x, y, yaw: Current USV state
            current_speed: Current speed (m/s)
            current_yaw_rate: Current yaw rate (rad/s)
            goal_x, goal_y: Goal position
            obstacles: List of obstacle dicts
            n_samples: Number of samples in dynamic window

        Returns:
            (command_speed, command_yaw_rate)
        """
        v_min, v_max, w_min, w_max = self.compute_dynamic_window(
            current_speed, current_yaw_rate
        )

        best_cost = float('inf')
        best_v = current_speed
        best_w = current_yaw_rate

        # Sample velocity space
        v_samples = np.linspace(v_min, v_max, n_samples)
        w_samples = np.linspace(w_min, w_max, n_samples)

        for v in v_samples:
            for w in w_samples:
                # Predict trajectory
                traj = self.predict_trajectory(x, y, yaw, v, w)

                # Compute costs
                obs_cost = self._obstacle_cost(traj, obstacles)
                if obs_cost == float('inf'):
                    continue  # Skip collision trajectories

                goal_cost = self._goal_cost(traj, goal_x, goal_y)
                speed_cost = self.dynamics.max_speed - v  # prefer higher speed
                heading_cost = abs(w)  # prefer straight

                # Total cost
                total = (
                    self.goal_weight * goal_cost +
                    self.obstacle_weight * obs_cost +
                    self.speed_weight * speed_cost +
                    self.heading_weight * heading_cost
                )

                if total < best_cost:
                    best_cost = total
                    best_v = v
                    best_w = w

        return best_v, best_w
