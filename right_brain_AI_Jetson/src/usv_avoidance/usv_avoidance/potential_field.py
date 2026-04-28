"""Artificial Potential Field Avoidance

Computes repulsive forces from obstacles and attractive force toward goal.
Used as secondary avoidance method alongside DWA.
"""

import numpy as np
from typing import List, Tuple


class PotentialFieldAvoidance:
    """Artificial Potential Field for USV Obstacle Avoidance"""

    def __init__(self, config: dict = None):
        config = config or {}
        self.attractive_gain = config.get("attractive_gain", 1.0)
        self.repulsive_gain = config.get("repulsive_gain", 100.0)
        self.influence_distance = config.get("influence_distance", 20.0)  # meters
        self.goal_threshold = config.get("goal_threshold", 2.0)

    def compute_attractive_force(self, usv_x: float, usv_y: float,
                                  goal_x: float, goal_y: float) -> Tuple[float, float]:
        """Compute attractive force toward goal"""
        dx = goal_x - usv_x
        dy = goal_y - usv_y
        dist = np.sqrt(dx*dx + dy*dy)

        if dist <= self.goal_threshold:
            # Conical potential near goal (avoid oscillation)
            fx = self.attractive_gain * dx / dist
            fy = self.attractive_gain * dy / dist
        else:
            # Quadratic potential far from goal
            fx = self.attractive_gain * dx
            fy = self.attractive_gain * dy

        return fx, fy

    def compute_repulsive_force(self, usv_x: float, usv_y: float,
                                 obstacles: List[dict]) -> Tuple[float, float]:
        """Compute repulsive force from all obstacles"""
        fx_total = 0.0
        fy_total = 0.0

        for obs in obstacles:
            ox = obs.get('x', 0.0)
            oy = obs.get('y', 0.0)

            dx = usv_x - ox
            dy = usv_y - oy
            dist = np.sqrt(dx*dx + dy*dy)

            if dist < 0.1:
                dist = 0.1  # avoid singularity

            if dist <= self.influence_distance:
                # Repulsive force magnitude
                magnitude = self.repulsive_gain * (
                    1.0 / dist - 1.0 / self.influence_distance
                ) / (dist * dist)

                # Force direction (away from obstacle)
                fx = magnitude * dx / dist
                fy = magnitude * dy / dist

                fx_total += fx
                fy_total += fy

        return fx_total, fy_total

    def compute_total_force(self, usv_x: float, usv_y: float,
                            goal_x: float, goal_y: float,
                            obstacles: List[dict]) -> Tuple[float, float]:
        """Compute total force (attractive + repulsive)"""
        fa_x, fa_y = self.compute_attractive_force(usv_x, usv_y, goal_x, goal_y)
        fr_x, fr_y = self.compute_repulsive_force(usv_x, usv_y, obstacles)

        return fa_x + fr_x, fa_y + fr_y

    def force_to_command(self, fx: float, fy: float,
                         current_yaw: float,
                         max_speed: float = 10.0) -> Tuple[float, float]:
        """Convert force vector to speed + yaw_rate command

        Returns:
            (speed, yaw_rate)
        """
        force_mag = np.sqrt(fx*fx + fy*fy)
        if force_mag < 0.01:
            return 0.0, 0.0

        # Desired heading from force direction
        desired_yaw = np.arctan2(fy, fx)

        # Yaw error
        yaw_error = desired_yaw - current_yaw
        yaw_error = np.arctan2(np.sin(yaw_error), np.cos(yaw_error))

        # Speed proportional to force magnitude, reduced when turning
        speed = min(force_mag * 0.5, max_speed) * np.cos(yaw_error)
        speed = max(speed, 0.0)

        # Yaw rate proportional to heading error
        yaw_rate = 2.0 * yaw_error

        return speed, yaw_rate
