"""ATR Pipeline - Orchestrates detection + tracking

Full pipeline: image input -> YOLO detection -> DeepSORT tracking -> output
"""

import numpy as np
import time
from typing import List, Optional
from .yolo_detector import YOLODetector, Detection
from .target_tracker import TargetTracker, TrackedTarget


class ATRPipeline:
    """Automatic Target Recognition Pipeline

    Combines YOLOv8 detection with DeepSORT tracking
    for real-time maritime target recognition.
    """

    def __init__(self, config: dict = None):
        config = config or {}

        # Sub-modules
        self.detector = YOLODetector(config.get("detector", {}))
        self.tracker = TargetTracker(config.get("tracker", {}))

        # Pipeline state
        self._frame_count = 0
        self._fps = 0.0
        self._last_fps_time = time.time()
        self._fps_frame_count = 0

    def initialize(self) -> bool:
        """Initialize pipeline (load models)"""
        return self.detector.load_model()

    def process(self, image: np.ndarray, timestamp: float = None) -> List[TrackedTarget]:
        """Process a single frame through the full ATR pipeline

        Args:
            image: BGR input image
            timestamp: Optional timestamp

        Returns:
            List of confirmed tracked targets
        """
        timestamp = timestamp or time.time()

        # Step 1: Detection
        detections = self.detector.detect(image)

        # Step 2: Tracking
        tracked = self.tracker.update(detections, timestamp)

        # Update FPS
        self._frame_count += 1
        self._fps_frame_count += 1
        now = time.time()
        dt = now - self._last_fps_time
        if dt >= 1.0:
            self._fps = self._fps_frame_count / dt
            self._fps_frame_count = 0
            self._last_fps_time = now

        return tracked

    def process_dual(self, visible: np.ndarray, ir: Optional[np.ndarray] = None,
                     alpha: float = 0.6) -> List[TrackedTarget]:
        """Process dual-light (visible + IR) images

        Args:
            visible: Visible light BGR image
            ir: IR BGR image (colormapped)
            alpha: Fusion weight

        Returns:
            List of confirmed tracked targets
        """
        # Detect on visible
        vis_dets = self.detector.detect(visible)

        # Detect on IR if available
        ir_dets = []
        if ir is not None:
            ir_dets = self.detector.detect(ir)

        # Merge detections (NMS across modalities)
        merged = self._merge_detections(vis_dets, ir_dets)

        # Track
        tracked = self.tracker.update(merged)
        return tracked

    def _merge_detections(self, vis_dets: List[Detection],
                          ir_dets: List[Detection]) -> List[Detection]:
        """Merge visible and IR detections with cross-modal NMS"""
        all_dets = vis_dets + ir_dets
        if not all_dets:
            return []

        # Sort by confidence
        all_dets.sort(key=lambda d: d.confidence, reverse=True)

        # Simple NMS
        keep = []
        while all_dets:
            best = all_dets.pop(0)
            keep.append(best)

            remaining = []
            for det in all_dets:
                iou = self._compute_iou(best.bbox, det.bbox)
                if iou < 0.5:  # IoU threshold for NMS
                    remaining.append(det)
            all_dets = remaining

        return keep

    @staticmethod
    def _compute_iou(box1: np.ndarray, box2: np.ndarray) -> float:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        if inter == 0:
            return 0.0
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        return inter / (area1 + area2 - inter)

    @property
    def fps(self) -> float:
        return self._fps

    def get_status(self) -> dict:
        """Get pipeline status"""
        return {
            "fps": round(self._fps, 1),
            "frame_count": self._frame_count,
            "active_tracks": len(self.tracker.tracks),
            "confirmed_tracks": len([
                t for t in self.tracker.tracks.values()
                if t.hits >= self.tracker.min_hits
            ]),
        }
