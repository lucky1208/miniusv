"""Occupancy Grid Map Builder

Builds 2D occupancy grid from fused sensor data for path planning.
Uses probabilistic occupancy update (log-odds) for robust mapping.
"""

import numpy as np
from typing import Optional, Tuple


class OccupancyMapBuilder:
    """2D Occupancy Grid Map for USV Navigation

    Grid resolution and size configurable for different operating ranges.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.resolution = config.get("resolution", 0.5)    # m/cell
        self.map_width = config.get("map_width", 400)       # cells
        self.map_height = config.get("map_height", 400)     # cells
        self.log_occ = config.get("log_occ", 0.7)           # log-odds hit
        self.log_free = config.get("log_free", -0.3)        # log-odds miss
        self.log_max = config.get("log_max", 5.0)           # clamp
        self.log_min = config.get("log_min", -5.0)          # clamp

        # Log-odds occupancy grid (0 = unknown)
        self.grid = np.zeros((self.map_height, self.map_width), dtype=np.float32)

        # Origin in world coordinates (center of grid)
        self.origin_x = -self.map_width * self.resolution / 2.0
        self.origin_y = -self.map_height * self.resolution / 2.0

    def world_to_grid(self, wx: float, wy: float) -> Tuple[int, int]:
        """Convert world coordinates to grid indices"""
        gx = int((wx - self.origin_x) / self.resolution)
        gy = int((wy - self.origin_y) / self.resolution)
        return gx, gy

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        """Convert grid indices to world coordinates"""
        wx = gx * self.resolution + self.origin_x + self.resolution / 2.0
        wy = gy * self.resolution + self.origin_y + self.resolution / 2.0
        return wx, wy

    def update_from_obstacles(self, obstacles: list, usv_x: float = 0.0, usv_y: float = 0.0):
        """Update occupancy grid from detected obstacles

        Args:
            obstacles: List of obstacle dicts with 'center' [x,y,z]
            usv_x, usv_y: USV position in world frame
        """
        for obs in obstacles:
            center = obs.get('center', [0, 0, 0])
            # Transform to world frame (relative to USV)
            wx = usv_x + center[0]
            wy = usv_y + center[1]

            gx, gy = self.world_to_grid(wx, wy)
            if 0 <= gx < self.map_width and 0 <= gy < self.map_height:
                # Mark occupied
                self.grid[gy, gx] = np.clip(
                    self.grid[gy, gx] + self.log_occ,
                    self.log_min, self.log_max
                )

                # Also mark cells around obstacle based on bbox
                bbox_min = obs.get('bbox_min', [0, 0, 0])
                bbox_max = obs.get('bbox_max', [0, 0, 0])
                min_gx, min_gy = self.world_to_grid(
                    usv_x + bbox_min[0], usv_y + bbox_min[1]
                )
                max_gx, max_gy = self.world_to_grid(
                    usv_x + bbox_max[0], usv_y + bbox_max[1]
                )
                for ix in range(max(0, min_gx), min(self.map_width, max_gx + 1)):
                    for iy in range(max(0, min_gy), min(self.map_height, max_gy + 1)):
                        self.grid[iy, ix] = np.clip(
                            self.grid[iy, ix] + self.log_occ,
                            self.log_min, self.log_max
                        )

    def raytrace_free(self, usv_x: float, usv_y: float,
                      target_x: float, target_y: float):
        """Mark cells along a ray as free (Bresenham's line)

        Used for clearing space between USV and detected obstacles.
        """
        gx0, gy0 = self.world_to_grid(usv_x, usv_y)
        gx1, gy1 = self.world_to_grid(target_x, target_y)

        # Bresenham's line algorithm
        dx = abs(gx1 - gx0)
        dy = abs(gy1 - gy0)
        sx = 1 if gx0 < gx1 else -1
        sy = 1 if gy0 < gy1 else -1
        err = dx - dy

        while True:
            if 0 <= gx0 < self.map_width and 0 <= gy0 < self.map_height:
                self.grid[gy0, gx0] = np.clip(
                    self.grid[gy0, gx0] + self.log_free,
                    self.log_min, self.log_max
                )

            if gx0 == gx1 and gy0 == gy1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                gx0 += sx
            if e2 < dx:
                err += dx
                gy0 += sy

    def get_probability_grid(self) -> np.ndarray:
        """Convert log-odds grid to probability [0, 1]"""
        return 1.0 - 1.0 / (1.0 + np.exp(self.grid))

    def is_occupied(self, wx: float, wy: float, threshold: float = 0.6) -> bool:
        """Check if a world coordinate is occupied"""
        gx, gy = self.world_to_grid(wx, wy)
        if 0 <= gx < self.map_width and 0 <= gy < self.map_height:
            prob = 1.0 - 1.0 / (1.0 + np.exp(self.grid[gy, gx]))
            return prob > threshold
        return True  # Out of map = occupied (safe)

    def get_grid_for_planning(self) -> np.ndarray:
        """Get binary occupancy grid for path planning (0=free, 1=occupied)"""
        prob_grid = self.get_probability_grid()
        return (prob_grid > 0.5).astype(np.uint8)

    def clear(self):
        """Reset the occupancy grid"""
        self.grid.fill(0)
