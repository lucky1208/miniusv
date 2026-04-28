"""A* Path Planner on Occupancy Grid

Global path planning using A* algorithm on 2D occupancy grid.
Supports 8-connected grid with diagonal movement.
"""

import numpy as np
import heapq
from typing import List, Optional, Tuple


class AStarPlanner:
    """A* Path Planner for USV Global Navigation

    Operates on 2D occupancy grid from SensorFusion module.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.allow_diagonal = config.get("allow_diagonal", True)
        self.obstacle_threshold = config.get("obstacle_threshold", 0.5)
        self.safety_margin = config.get("safety_margin", 2)  # cells to inflate obstacles
        self.max_iterations = config.get("max_iterations", 100000)

        # 8-connected movement: (dx, dy, cost)
        self.movements = [
            (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        ]
        if self.allow_diagonal:
            self.movements.extend([
                (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414),
            ])

    def _inflate_obstacles(self, grid: np.ndarray) -> np.ndarray:
        """Inflate obstacles by safety margin for collision-free planning"""
        if self.safety_margin <= 0:
            return grid

        inflated = grid.copy()
        h, w = grid.shape
        margin = self.safety_margin

        # Find occupied cells
        occupied = np.argwhere(grid > self.obstacle_threshold)

        for oy, ox in occupied:
            y_min = max(0, oy - margin)
            y_max = min(h, oy + margin + 1)
            x_min = max(0, ox - margin)
            x_max = min(w, ox + margin + 1)
            inflated[y_min:y_max, x_min:x_max] = 1.0

        return inflated

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Octile distance heuristic (admissible for 8-connected grid)"""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)

    def plan(self, grid: np.ndarray,
             start: Tuple[int, int],
             goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Plan path from start to goal on occupancy grid

        Args:
            grid: 2D occupancy grid (0=free, 1=occupied)
            start: (x, y) grid coordinates
            goal: (x, y) grid coordinates

        Returns:
            List of (x, y) waypoints from start to goal, or None if no path
        """
        h, w = grid.shape

        # Inflate obstacles
        inflated = self._inflate_obstacles(grid)

        # Check start and goal validity
        sx, sy = start
        gx, gy = goal
        if not (0 <= sx < w and 0 <= sy < h and inflated[sy, sx] <= self.obstacle_threshold):
            return None
        if not (0 <= gx < w and 0 <= gy < h and inflated[gy, gx] <= self.obstacle_threshold):
            return None

        # A* search
        open_set = []
        heapq.heappush(open_set, (0.0, start))

        came_from = {}
        g_score = {start: 0.0}
        closed_set = set()

        iterations = 0
        while open_set and iterations < self.max_iterations:
            iterations += 1
            _, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            if current in closed_set:
                continue
            closed_set.add(current)

            cx, cy = current
            for dx, dy, cost in self.movements:
                nx, ny = cx + dx, cy + dy

                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if inflated[ny, nx] > self.obstacle_threshold:
                    continue
                if (nx, ny) in closed_set:
                    continue

                tentative_g = g_score[current] + cost

                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    g_score[(nx, ny)] = tentative_g
                    f = tentative_g + self._heuristic((nx, ny), goal)
                    came_from[(nx, ny)] = current
                    heapq.heappush(open_set, (f, (nx, ny)))

        return None  # No path found

    def plan_world(self, grid: np.ndarray, resolution: float,
                   origin: Tuple[float, float],
                   start_world: Tuple[float, float],
                   goal_world: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """Plan path in world coordinates

        Args:
            grid: Occupancy grid
            resolution: m/cell
            origin: (ox, oy) world coordinates of grid origin
            start_world: (x, y) world coordinates
            goal_world: (x, y) world coordinates

        Returns:
            Path in world coordinates, or None
        """
        # Convert to grid coordinates
        start_grid = (
            int((start_world[0] - origin[0]) / resolution),
            int((start_world[1] - origin[1]) / resolution)
        )
        goal_grid = (
            int((goal_world[0] - origin[0]) / resolution),
            int((goal_world[1] - origin[1]) / resolution)
        )

        grid_path = self.plan(grid, start_grid, goal_grid)
        if grid_path is None:
            return None

        # Convert back to world coordinates
        world_path = [
            (gx * resolution + origin[0] + resolution / 2,
             gy * resolution + origin[1] + resolution / 2)
            for gx, gy in grid_path
        ]
        return world_path

    def smooth_path(self, path: List[Tuple[float, float]],
                    weight_smooth: float = 0.3,
                    tolerance: float = 0.001) -> List[Tuple[float, float]]:
        """Gradient descent path smoothing

        Args:
            path: List of (x, y) waypoints
            weight_smooth: Smoothing weight
            tolerance: Convergence tolerance

        Returns:
            Smoothed path
        """
        if len(path) <= 2:
            return path

        new_path = [list(p) for p in path]
        change = tolerance + 1

        while change > tolerance:
            change = 0.0
            for i in range(1, len(new_path) - 1):
                for j in range(2):
                    old = new_path[i][j]
                    new_path[i][j] += weight_smooth * (
                        new_path[i-1][j] + new_path[i+1][j] - 2.0 * new_path[i][j]
                    )
                    change += abs(old - new_path[i][j])

        return [tuple(p) for p in new_path]
