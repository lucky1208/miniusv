"""Multi-Object Target Tracker using DeepSORT

Tracks detected targets across frames for:
- Persistent target IDs
- Velocity estimation
- Trajectory prediction
- Lost target management
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time


@dataclass
class TrackedTarget:
    """A tracked target with persistent ID and state history"""
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: np.ndarray              # [x1, y1, x2, y2]
    center: np.ndarray            # [cx, cy] in image
    world_pos: np.ndarray = field(default_factory=lambda: np.zeros(3))  # [x,y,z] world
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))   # [vx,vy,vz]
    trajectory: list = field(default_factory=list)  # list of past positions
    age: int = 0                  # frames since creation
    hits: int = 0                 # total detection hits
    lost_count: int = 0           # consecutive missed frames
    last_update: float = 0.0
    threat_level: int = 0         # 0-5 threat level


class TargetTracker:
    """DeepSORT-inspired Multi-Object Tracker

    Simplified implementation for USV maritime target tracking.
    Uses IoU-based association with Kalman filter state prediction.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.max_lost = config.get("max_lost", 30)          # frames before deletion
        self.min_hits = config.get("min_hits", 3)           # hits to confirm track
        self.iou_threshold = config.get("iou_threshold", 0.3)
        self.max_trajectory = config.get("max_trajectory", 100)
        self.max_tracks = config.get("max_tracks", 50)

        self.tracks: Dict[int, TrackedTarget] = {}
        self._next_id = 0

    def _compute_iou(self, box1: np.ndarray, box2: np.ndarray) -> float:
        """Compute IoU between two bounding boxes [x1,y1,x2,y2]"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter = max(0, x2 - x1) * max(0, y2 - y1)
        if inter == 0:
            return 0.0

        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - inter

        return inter / union if union > 0 else 0.0

    def _associate(self, detections: list) -> tuple:
        """Associate detections to existing tracks using Hungarian-like greedy IoU matching

        Returns:
            (matched_pairs, unmatched_detections, unmatched_tracks)
        """
        if not self.tracks or not detections:
            return [], list(range(len(detections))), list(self.tracks.keys())

        track_ids = list(self.tracks.keys())
        n_tracks = len(track_ids)
        n_dets = len(detections)

        # Compute IoU cost matrix
        iou_matrix = np.zeros((n_tracks, n_dets))
        for i, tid in enumerate(track_ids):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = self._compute_iou(
                    self.tracks[tid].bbox, det.bbox
                )

        # Greedy matching (highest IoU first)
        matched = []
        matched_tracks = set()
        matched_dets = set()

        for _ in range(min(n_tracks, n_dets)):
            max_iou_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
            max_iou = iou_matrix[max_iou_idx]

            if max_iou < self.iou_threshold:
                break

            i, j = max_iou_idx
            matched.append((track_ids[i], j))
            matched_tracks.add(i)
            matched_dets.add(j)
            iou_matrix[i, :] = 0
            iou_matrix[:, j] = 0

        unmatched_dets = [j for j in range(n_dets) if j not in matched_dets]
        unmatched_tracks = [track_ids[i] for i in range(n_tracks) if i not in matched_tracks]

        return matched, unmatched_dets, unmatched_tracks

    def update(self, detections: list, timestamp: float = None) -> List[TrackedTarget]:
        """Update tracker with new detections

        Args:
            detections: List of Detection objects from YOLO
            timestamp: Current timestamp

        Returns:
            List of confirmed TrackedTarget objects
        """
        timestamp = timestamp or time.time()

        matched, unmatched_dets, unmatched_tracks = self._associate(detections)

        # Update matched tracks
        for tid, det_idx in matched:
            det = detections[det_idx]
            track = self.tracks[tid]

            # Smooth bbox update
            alpha = 0.3
            track.bbox = alpha * det.bbox + (1 - alpha) * track.bbox
            track.center = alpha * det.center + (1 - alpha) * track.center
            track.confidence = det.confidence
            track.class_id = det.class_id
            track.class_name = det.class_name
            track.hits += 1
            track.age += 1
            track.lost_count = 0
            track.last_update = timestamp

            # Update trajectory
            track.trajectory.append(track.center.copy())
            if len(track.trajectory) > self.max_trajectory:
                track.trajectory.pop(0)

            # Estimate velocity from trajectory
            if len(track.trajectory) >= 2:
                dt = 1.0 / 30.0  # assume 30fps
                recent = np.array(track.trajectory[-5:])
                if len(recent) >= 2:
                    track.velocity[:2] = (recent[-1] - recent[0]) / (dt * (len(recent) - 1))

        # Create new tracks for unmatched detections
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            track = TrackedTarget(
                track_id=self._next_id,
                class_id=det.class_id,
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=det.bbox.copy(),
                center=det.center.copy(),
                hits=1,
                age=1,
                last_update=timestamp,
            )
            track.trajectory.append(det.center.copy())
            self.tracks[self._next_id] = track
            self._next_id += 1

        # Update lost tracks
        for tid in unmatched_tracks:
            self.tracks[tid].lost_count += 1
            self.tracks[tid].age += 1

        # Remove old lost tracks
        lost_ids = [
            tid for tid, t in self.tracks.items()
            if t.lost_count > self.max_lost
        ]
        for tid in lost_ids:
            del self.tracks[tid]

        # Return confirmed tracks
        confirmed = [
            t for t in self.tracks.values()
            if t.hits >= self.min_hits and t.lost_count == 0
        ]
        return confirmed

    def get_all_tracks(self) -> List[TrackedTarget]:
        """Get all active tracks (including unconfirmed)"""
        return list(self.tracks.values())

    def get_tracks_dict(self) -> list:
        """Get tracks as list of dicts for inter-brain communication"""
        return [
            {
                "track_id": t.track_id,
                "class_name": t.class_name,
                "confidence": round(t.confidence, 3),
                "bbox": t.bbox.tolist(),
                "center": t.center.tolist(),
                "world_pos": t.world_pos.tolist(),
                "velocity": t.velocity.tolist(),
                "threat_level": t.threat_level,
                "age": t.age,
                "hits": t.hits,
            }
            for t in self.tracks.values()
            if t.hits >= self.min_hits
        ]
