"""Millimeter-Wave Radar Processor for USV

Processes 77GHz mmWave radar data:
- Target detection and tracking
- Range-Doppler processing
- Dynamic target list management
- Radar-LiDAR track association
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time


@dataclass
class RadarTarget:
    """Single radar tracked target"""
    track_id: int
    range_m: float              # radial distance (m)
    azimuth_rad: float          # azimuth angle (rad)
    elevation_rad: float        # elevation angle (rad)
    radial_velocity: float      # radial velocity (m/s)
    rcs: float                  # radar cross section (m²)
    x: float = 0.0             # Cartesian x (m)
    y: float = 0.0             # Cartesian y (m)
    z: float = 0.0             # Cartesian z (m)
    vx: float = 0.0            # velocity x (m/s)
    vy: float = 0.0            # velocity y (m/s)
    last_update: float = 0.0   # timestamp
    age: int = 0               # number of updates
    lost_count: int = 0        # consecutive missed detections


class RadarProcessor:
    """77GHz Millimeter-Wave Radar Processor

    Specs (from design doc):
    - Frequency: 77GHz
    - Detection range: 200m (vessel), 100m (person)
    - Range resolution: 0.5m
    - Velocity resolution: 0.1m/s
    - Angle resolution: 1°
    - FOV: 120°(H) × 30°(V)
    - Update rate: 20Hz
    - Max tracked targets: 64
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.max_range = config.get("max_range", 200.0)
        self.min_range = config.get("min_range", 1.0)
        self.max_targets = config.get("max_targets", 64)
        self.track_timeout = config.get("track_timeout", 0.5)  # seconds
        self.gating_threshold = config.get("gating_threshold", 3.0)  # Mahalanobis distance
        self.max_lost_count = config.get("max_lost_count", 5)

        # Track management
        self.tracks: Dict[int, RadarTarget] = {}
        self._next_track_id = 0

    def polar_to_cartesian(self, target: RadarTarget) -> RadarTarget:
        """Convert polar radar measurement to Cartesian coordinates"""
        cos_el = np.cos(target.elevation_rad)
        target.x = target.range_m * np.cos(target.azimuth_rad) * cos_el
        target.y = target.range_m * np.sin(target.azimuth_rad) * cos_el
        target.z = target.range_m * np.sin(target.elevation_rad)

        # Estimate Cartesian velocity from radial velocity
        if target.range_m > 0.01:
            cos_az = np.cos(target.azimuth_rad)
            sin_az = np.sin(target.azimuth_rad)
            target.vx = target.radial_velocity * cos_az
            target.vy = target.radial_velocity * sin_az

        return target

    def update_tracks(self, detections: List[RadarTarget], timestamp: float) -> List[RadarTarget]:
        """Update track list with new detections using nearest-neighbor association

        Args:
            detections: New radar detections from current scan
            timestamp: Current timestamp

        Returns:
            Updated list of active tracks
        """
        # Convert all detections to Cartesian
        for det in detections:
            self.polar_to_cartesian(det)

        # Track-to-detection association (greedy nearest-neighbor)
        associated_detections = set()
        associated_tracks = set()

        # Compute cost matrix
        if self.tracks and detections:
            track_ids = list(self.tracks.keys())
            cost_matrix = np.full((len(track_ids), len(detections)), np.inf)

            for i, tid in enumerate(track_ids):
                track = self.tracks[tid]
                for j, det in enumerate(detections):
                    dx = track.x - det.x
                    dy = track.y - det.y
                    dist = np.sqrt(dx*dx + dy*dy)
                    cost_matrix[i, j] = dist

            # Greedy assignment
            for _ in range(min(len(track_ids), len(detections))):
                min_idx = np.unravel_index(np.argmin(cost_matrix), cost_matrix.shape)
                if cost_matrix[min_idx] > self.gating_threshold:
                    break

                i, j = min_idx
                tid = track_ids[i]
                det = detections[j]

                # Update existing track with detection (alpha-beta filter)
                alpha = 0.3
                beta = 0.1
                track = self.tracks[tid]
                dt = timestamp - track.last_update if track.last_update > 0 else 0.05

                # Position update
                track.x = track.x + alpha * (det.x - track.x)
                track.y = track.y + alpha * (det.y - track.y)
                track.z = track.z + alpha * (det.z - track.z)

                # Velocity update
                track.vx = track.vx + beta * (det.x - track.x) / dt if dt > 0 else track.vx
                track.vy = track.vy + beta * (det.y - track.y) / dt if dt > 0 else track.vy

                track.range_m = det.range_m
                track.azimuth_rad = det.azimuth_rad
                track.elevation_rad = det.elevation_rad
                track.radial_velocity = det.radial_velocity
                track.rcs = det.rcs
                track.last_update = timestamp
                track.age += 1
                track.lost_count = 0

                associated_tracks.add(i)
                associated_detections.add(j)
                cost_matrix[i, :] = np.inf
                cost_matrix[:, j] = np.inf

        # Create new tracks for unassociated detections
        for j, det in enumerate(detections):
            if j not in associated_detections:
                det.track_id = self._next_track_id
                det.last_update = timestamp
                det.age = 1
                det.lost_count = 0
                self.tracks[self._next_track_id] = det
                self._next_track_id += 1

        # Increment lost count for unassociated tracks
        for i, tid in enumerate(list(self.tracks.keys())):
            if tid not in [list(self.tracks.keys())[k] for k in associated_tracks]:
                self.tracks[tid].lost_count += 1

        # Remove lost tracks
        lost_ids = [
            tid for tid, track in self.tracks.items()
            if track.lost_count > self.max_lost_count
        ]
        for tid in lost_ids:
            del self.tracks[tid]

        # Limit total tracks
        if len(self.tracks) > self.max_targets:
            sorted_tracks = sorted(
                self.tracks.items(),
                key=lambda x: x[1].lost_count - x[1].age
            )
            self.tracks = dict(sorted_tracks[:self.max_targets])

        return list(self.tracks.values())

    def get_target_list(self) -> List[dict]:
        """Get target list as dict for inter-brain communication"""
        return [
            {
                "track_id": t.track_id,
                "x": round(t.x, 2),
                "y": round(t.y, 2),
                "z": round(t.z, 2),
                "vx": round(t.vx, 2),
                "vy": round(t.vy, 2),
                "range": round(t.range_m, 2),
                "azimuth": round(np.degrees(t.azimuth_rad), 1),
                "radial_vel": round(t.radial_velocity, 2),
                "rcs": round(t.rcs, 3),
                "age": t.age,
            }
            for t in self.tracks.values()
            if t.lost_count == 0
        ]
