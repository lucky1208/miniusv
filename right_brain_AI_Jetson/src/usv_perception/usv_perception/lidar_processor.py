"""LiDAR Point Cloud Processor for USV

Processes 360° solid-state LiDAR data (Ouster OS1-64 equivalent):
- Point cloud filtering (ground removal, noise)
- Obstacle clustering (DBSCAN)
- Obstacle bounding box extraction
- Water surface segmentation
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
from sklearn.cluster import DBSCAN


@dataclass
class Obstacle:
    """Detected obstacle from LiDAR"""
    id: int
    center: np.ndarray          # [x, y, z] in vehicle frame
    bbox_min: np.ndarray        # bounding box min corner
    bbox_max: np.ndarray        # bounding box max corner
    point_count: int            # number of points in cluster
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))  # estimated velocity
    obstacle_type: str = "unknown"  # vessel, buoy, debris, unknown
    confidence: float = 0.0


class LidarProcessor:
    """360° Solid-State LiDAR Processor

    Specs (from design doc):
    - 16-line mechanical rotating / 64-line solid-state
    - Detection range: 100m (10% reflectivity)
    - Range accuracy: ±3cm
    - Horizontal FOV: 360°
    - Vertical FOV: 30° (-15° ~ +15°)
    - Scan rate: 10Hz
    - Point density: 300,000 pts/s
    """

    def __init__(self, config: dict = None):
        config = config or {}
        # Processing parameters
        self.min_range = config.get("min_range", 0.5)       # meters
        self.max_range = config.get("max_range", 100.0)     # meters
        self.ground_threshold = config.get("ground_threshold", 0.15)  # meters
        self.cluster_eps = config.get("cluster_eps", 1.5)    # DBSCAN epsilon
        self.cluster_min_samples = config.get("cluster_min_samples", 10)
        self.water_level = config.get("water_level", -0.2)   # estimated water surface z
        self.voxel_size = config.get("voxel_size", 0.2)      # downsampling voxel size

        # State
        self.obstacles: List[Obstacle] = []
        self._obstacle_id_counter = 0

    def filter_point_cloud(self, points: np.ndarray) -> np.ndarray:
        """Filter raw point cloud: range filter + ground removal + noise

        Args:
            points: Nx4 array [x, y, z, intensity] or Nx3 [x, y, z]

        Returns:
            Filtered point cloud (non-ground, in-range points)
        """
        if points.shape[0] == 0:
            return points

        xyz = points[:, :3]

        # Range filter
        ranges = np.linalg.norm(xyz, axis=1)
        range_mask = (ranges >= self.min_range) & (ranges <= self.max_range)

        # Ground removal: points near or below water surface are ground
        ground_mask = xyz[:, 2] > (self.water_level + self.ground_threshold)

        # Combined mask
        mask = range_mask & ground_mask
        return points[mask]

    def voxel_downsample(self, points: np.ndarray) -> np.ndarray:
        """Voxel grid downsampling for performance

        Args:
            points: Nx3 or Nx4 array

        Returns:
            Downsampled point cloud
        """
        if points.shape[0] == 0:
            return points

        xyz = points[:, :3]
        # Compute voxel indices
        voxel_indices = np.floor(xyz / self.voxel_size).astype(np.int32)

        # Use lexsort to find unique voxels, keep first point in each voxel
        sorted_idx = np.lexsort(voxel_indices[:, ::-1].T)
        sorted_voxels = voxel_indices[sorted_idx]

        # Find unique voxel boundaries
        diff = np.diff(sorted_voxels, axis=0)
        unique_mask = np.any(diff != 0, axis=1)
        unique_mask = np.concatenate([[True], unique_mask])

        return points[sorted_idx[unique_mask]]

    def cluster_obstacles(self, points: np.ndarray) -> List[Obstacle]:
        """DBSCAN clustering to identify individual obstacles

        Args:
            points: Nx3+ filtered point cloud

        Returns:
            List of detected Obstacle objects
        """
        if points.shape[0] < self.cluster_min_samples:
            return []

        xyz = points[:, :3]

        # Run DBSCAN clustering
        clustering = DBSCAN(
            eps=self.cluster_eps,
            min_samples=self.cluster_min_samples
        ).fit(xyz)

        labels = clustering.labels_
        unique_labels = set(labels) - {-1}  # exclude noise

        obstacles = []
        for label in unique_labels:
            cluster_mask = labels == label
            cluster_points = xyz[cluster_mask]

            if len(cluster_points) < self.cluster_min_samples:
                continue

            center = np.mean(cluster_points, axis=0)
            bbox_min = np.min(cluster_points, axis=0)
            bbox_max = np.max(cluster_points, axis=0)

            # Classify obstacle by size
            size = bbox_max - bbox_min
            obs_type = self._classify_by_size(size)

            obstacle = Obstacle(
                id=self._obstacle_id_counter,
                center=center,
                bbox_min=bbox_min,
                bbox_max=bbox_max,
                point_count=len(cluster_points),
                obstacle_type=obs_type,
                confidence=min(len(cluster_points) / 100.0, 1.0)
            )
            self._obstacle_id_counter += 1
            obstacles.append(obstacle)

        self.obstacles = obstacles
        return obstacles

    def _classify_by_size(self, size: np.ndarray) -> str:
        """Rough obstacle classification by bounding box size

        Args:
            size: [dx, dy, dz] bounding box dimensions

        Returns:
            Obstacle type string
        """
        length = max(size[0], size[1])
        height = size[2]

        if length > 10.0 and height > 2.0:
            return "large_vessel"
        elif length > 3.0 and height > 1.0:
            return "vessel"
        elif length > 1.0 and height < 1.0:
            return "buoy"
        elif length < 1.0 and height < 0.5:
            return "debris"
        else:
            return "unknown"

    def process(self, raw_points: np.ndarray) -> List[Obstacle]:
        """Full processing pipeline: filter -> downsample -> cluster

        Args:
            raw_points: Raw point cloud from LiDAR driver

        Returns:
            List of detected obstacles
        """
        filtered = self.filter_point_cloud(raw_points)
        downsampled = self.voxel_downsample(filtered)
        obstacles = self.cluster_obstacles(downsampled)
        return obstacles

    def get_obstacle_map(self) -> dict:
        """Get obstacle data as dict for inter-brain communication"""
        return {
            "timestamp": np.datetime64('now').astype(np.int64),
            "obstacles": [
                {
                    "id": obs.id,
                    "center": obs.center.tolist(),
                    "bbox_min": obs.bbox_min.tolist(),
                    "bbox_max": obs.bbox_max.tolist(),
                    "type": obs.obstacle_type,
                    "confidence": obs.confidence,
                    "velocity": obs.velocity.tolist(),
                }
                for obs in self.obstacles
            ]
        }
