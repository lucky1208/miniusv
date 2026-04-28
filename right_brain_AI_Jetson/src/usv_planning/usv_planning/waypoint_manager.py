"""Waypoint Manager for USV Mission Navigation

Manages waypoint lists, progress tracking, and arrival detection.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import time


@dataclass
class Waypoint:
    """Navigation waypoint"""
    x: float                    # East (m)
    y: float                    # North (m)
    z: float = 0.0             # Up (m)
    speed: float = 5.0         # target speed (m/s)
    heading: Optional[float] = None  # target heading (rad), None = auto
    radius: float = 3.0        # arrival radius (m)
    id: int = 0
    visited: bool = False
    timestamp: float = 0.0     # time when visited


class WaypointManager:
    """Waypoint Management for USV

    Handles waypoint sequencing, arrival detection,
    and mission progress tracking.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.default_speed = config.get("default_speed", 5.0)     # m/s
        self.default_radius = config.get("default_radius", 3.0)   # m
        self.loop_mission = config.get("loop_mission", False)     # repeat mission

        self.waypoints: List[Waypoint] = []
        self.current_idx: int = 0
        self.mission_complete: bool = False

    def load_waypoints(self, wp_list: List[dict]):
        """Load waypoints from list of dicts

        Args:
            wp_list: [{'x': ..., 'y': ..., 'speed': ..., ...}, ...]
        """
        self.waypoints = []
        for i, wp in enumerate(wp_list):
            self.waypoints.append(Waypoint(
                x=wp['x'],
                y=wp['y'],
                z=wp.get('z', 0.0),
                speed=wp.get('speed', self.default_speed),
                heading=wp.get('heading', None),
                radius=wp.get('radius', self.default_radius),
                id=i,
            ))
        self.current_idx = 0
        self.mission_complete = False

    def get_current_waypoint(self) -> Optional[Waypoint]:
        """Get current target waypoint"""
        if self.mission_complete or not self.waypoints:
            return None
        if self.current_idx < len(self.waypoints):
            return self.waypoints[self.current_idx]
        return None

    def check_arrival(self, usv_x: float, usv_y: float) -> bool:
        """Check if USV has arrived at current waypoint

        Args:
            usv_x, usv_y: USV position (m)

        Returns:
            True if arrived at current waypoint
        """
        wp = self.get_current_waypoint()
        if wp is None:
            return False

        dist = np.sqrt((usv_x - wp.x)**2 + (usv_y - wp.y)**2)
        if dist <= wp.radius:
            wp.visited = True
            wp.timestamp = time.time()
            self._advance()
            return True
        return False

    def _advance(self):
        """Advance to next waypoint"""
        self.current_idx += 1
        if self.current_idx >= len(self.waypoints):
            if self.loop_mission:
                self.current_idx = 0
                for wp in self.waypoints:
                    wp.visited = False
            else:
                self.mission_complete = True

    def get_progress(self) -> dict:
        """Get mission progress info"""
        total = len(self.waypoints)
        visited = sum(1 for wp in self.waypoints if wp.visited)
        return {
            "total_waypoints": total,
            "visited": visited,
            "current_idx": self.current_idx,
            "progress_pct": round(visited / total * 100, 1) if total > 0 else 0,
            "mission_complete": self.mission_complete,
        }

    def get_path_points(self) -> List[Tuple[float, float]]:
        """Get all waypoint positions as path for visualization"""
        return [(wp.x, wp.y) for wp in self.waypoints]

    def get_remaining_path(self) -> List[Tuple[float, float]]:
        """Get remaining unvisited waypoints"""
        return [
            (wp.x, wp.y)
            for wp in self.waypoints[self.current_idx:]
        ]
