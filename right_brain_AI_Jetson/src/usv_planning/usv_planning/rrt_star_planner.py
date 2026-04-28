"""RRT* Path Planner for Dynamic Replanning

Local path planning using RRT* for:
- Dynamic obstacle avoidance
- Smooth path generation
- Continuous replanning at 5-10Hz
"""

import numpy as np
import random
import math
from typing import List, Optional, Tuple


class RRTNode:
    """RRT tree node"""
    def __init__(self, x: float, y: float, parent: int = -1, cost: float = 0.0):
        self.x = x
        self.y = y
        self.parent = parent
        self.cost = cost


class RRTStarPlanner:
    """RRT* Path Planner for USV Local Navigation

    Used for dynamic replanning when obstacles are detected
    along the global A* path.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.step_size = config.get("step_size", 2.0)        # meters
        self.max_iter = config.get("max_iter", 500)
        self.goal_threshold = config.get("goal_threshold", 3.0)  # meters
        self.search_radius = config.get("search_radius", 10.0)  # meters for rewiring
        self.goal_bias = config.get("goal_bias", 0.1)        # probability of sampling goal
        self.x_min = config.get("x_min", -100.0)
        self.x_max = config.get("x_max", 100.0)
        self.y_min = config.get("y_min", -100.0)
        self.y_max = config.get("y_max", 100.0)

    def _collision_free(self, p1: Tuple[float, float],
                        p2: Tuple[float, float],
                        occupancy_grid: np.ndarray,
                        resolution: float,
                        origin: Tuple[float, float]) -> bool:
        """Check if line segment p1->p2 is collision-free

        Uses Bresenham-like interpolation on occupancy grid
        """
        dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
        n_steps = max(int(dist / (resolution * 0.5)), 2)

        for i in range(n_steps + 1):
            t = i / n_steps
            x = p1[0] + t * (p2[0] - p1[0])
            y = p1[1] + t * (p2[1] - p1[1])

            # Convert to grid
            gx = int((x - origin[0]) / resolution)
            gy = int((y - origin[1]) / resolution)

            h, w = occupancy_grid.shape
            if 0 <= gx < w and 0 <= gy < h:
                if occupancy_grid[gy, gx] > 0.5:
                    return False
            else:
                return False  # Out of bounds = blocked

        return True

    def _nearest(self, nodes: List[RRTNode], point: Tuple[float, float]) -> int:
        """Find nearest node to point"""
        min_dist = float('inf')
        min_idx = 0
        for i, node in enumerate(nodes):
            d = (node.x - point[0])**2 + (node.y - point[1])**2
            if d < min_dist:
                min_dist = d
                min_idx = i
        return min_idx

    def _steer(self, from_node: RRTNode, to_point: Tuple[float, float]) -> Tuple[float, float]:
        """Steer from node towards point with step_size limit"""
        dx = to_point[0] - from_node.x
        dy = to_point[1] - from_node.y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist <= self.step_size:
            return to_point

        ratio = self.step_size / dist
        return (from_node.x + dx * ratio, from_node.y + dy * ratio)

    def _near_nodes(self, nodes: List[RRTNode], point: Tuple[float, float]) -> List[int]:
        """Find nodes within search_radius of point"""
        r2 = self.search_radius ** 2
        return [
            i for i, n in enumerate(nodes)
            if (n.x - point[0])**2 + (n.y - point[1])**2 <= r2
        ]

    def plan(self, start: Tuple[float, float],
             goal: Tuple[float, float],
             occupancy_grid: np.ndarray,
             resolution: float = 0.5,
             origin: Tuple[float, float] = (0.0, 0.0)) -> Optional[List[Tuple[float, float]]]:
        """Plan path using RRT*

        Args:
            start: (x, y) world coordinates
            goal: (x, y) world coordinates
            occupancy_grid: 2D grid (0=free, 1=occupied)
            resolution: m/cell
            origin: grid origin in world frame

        Returns:
            Path as list of (x, y) waypoints, or None
        """
        nodes = [RRTNode(start[0], start[1], parent=-1, cost=0.0)]

        for iteration in range(self.max_iter):
            # Sample random point (with goal bias)
            if random.random() < self.goal_bias:
                rand_point = goal
            else:
                rand_point = (
                    random.uniform(self.x_min, self.x_max),
                    random.uniform(self.y_min, self.y_max),
                )

            # Find nearest node
            nearest_idx = self._nearest(nodes, rand_point)
            nearest_node = nodes[nearest_idx]

            # Steer towards random point
            new_point = self._steer(nearest_node, rand_point)

            # Check collision
            if not self._collision_free(
                (nearest_node.x, nearest_node.y), new_point,
                occupancy_grid, resolution, origin
            ):
                continue

            # Find nearby nodes for rewiring
            near_indices = self._near_nodes(nodes, new_point)

            # Choose best parent
            min_cost = nearest_node.cost + math.sqrt(
                (new_point[0]-nearest_node.x)**2 + (new_point[1]-nearest_node.y)**2
            )
            best_parent = nearest_idx

            for near_idx in near_indices:
                near_node = nodes[near_idx]
                new_cost = near_node.cost + math.sqrt(
                    (new_point[0]-near_node.x)**2 + (new_point[1]-near_node.y)**2
                )
                if new_cost < min_cost:
                    if self._collision_free(
                        (near_node.x, near_node.y), new_point,
                        occupancy_grid, resolution, origin
                    ):
                        min_cost = new_cost
                        best_parent = near_idx

            # Add new node
            new_node = RRTNode(new_point[0], new_point[1],
                               parent=best_parent, cost=min_cost)
            nodes.append(new_node)
            new_idx = len(nodes) - 1

            # Rewire nearby nodes
            for near_idx in near_indices:
                near_node = nodes[near_idx]
                rewire_cost = new_node.cost + math.sqrt(
                    (near_node.x-new_node.x)**2 + (near_node.y-new_node.y)**2
                )
                if rewire_cost < near_node.cost:
                    if self._collision_free(
                        (new_node.x, new_node.y), (near_node.x, near_node.y),
                        occupancy_grid, resolution, origin
                    ):
                        nodes[near_idx].parent = new_idx
                        nodes[near_idx].cost = rewire_cost

            # Check if goal reached
            dist_to_goal = math.sqrt(
                (new_point[0]-goal[0])**2 + (new_point[1]-goal[1])**2
            )
            if dist_to_goal <= self.goal_threshold:
                # Reconstruct path
                path = []
                idx = new_idx
                while idx != -1:
                    path.append((nodes[idx].x, nodes[idx].y))
                    idx = nodes[idx].parent
                path.reverse()
                path.append(goal)
                return path

        return None  # No path found within max iterations
