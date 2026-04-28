"""YOLOv8 Maritime Target Detector

Runs YOLOv8 on Jetson Orin NX GPU (TensorRT accelerated) for:
- Real-time vessel detection
- Buoy and navigation mark detection
- Debris and floating object detection
- Person-in-water detection

Target classes (maritime-specific):
0: fishing_vessel    1: cargo_ship    2: tanker
3: speedboat         4: warship      5: buoy
6: navigation_mark   7: debris       8: person_in_water
9: kayak_small       10: sailboat    11: unknown_vessel
"""

import numpy as np
import cv2
import time
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class Detection:
    """Single detection result"""
    class_id: int
    class_name: str
    confidence: float
    bbox: np.ndarray          # [x1, y1, x2, y2] pixel coords
    center: np.ndarray = field(default_factory=lambda: np.zeros(2))
    width: float = 0.0
    height: float = 0.0


# Maritime target class names
MARITIME_CLASSES = [
    "fishing_vessel", "cargo_ship", "tanker",
    "speedboat", "warship", "buoy",
    "navigation_mark", "debris", "person_in_water",
    "kayak_small", "sailboat", "unknown_vessel"
]


class YOLODetector:
    """YOLOv8 Maritime Target Detector with TensorRT acceleration

    Specs (from design doc):
    - Model: YOLOv8 + ResNet50 ensemble
    - Accuracy: >95% (vessel)
    - Speed: 30fps on Jetson Orin NX
    - Input: 640x480 BGR
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.model_path = config.get(
            "model_path",
            "models/yolov8_maritime_trt.engine"
        )
        self.conf_threshold = config.get("conf_threshold", 0.5)
        self.iou_threshold = config.get("iou_threshold", 0.45)
        self.input_size = config.get("input_size", (640, 480))
        self.max_detections = config.get("max_detections", 100)
        self.class_names = config.get("class_names", MARITIME_CLASSES)

        self.model = None
        self._use_tensorrt = False
        self._use_onnx = False

    def load_model(self) -> bool:
        """Load YOLOv8 model with TensorRT > ONNX > PyTorch fallback

        Returns:
            True if model loaded successfully
        """
        model_path = Path(self.model_path)

        # Try TensorRT engine first (fastest on Jetson)
        if model_path.suffix == '.engine' and model_path.exists():
            try:
                self._load_tensorrt(str(model_path))
                self._use_tensorrt = True
                print(f"[YOLODetector] Loaded TensorRT engine: {model_path}")
                return True
            except Exception as e:
                print(f"[YOLODetector] TensorRT load failed: {e}")

        # Try ONNX runtime
        onnx_path = str(model_path).replace('.engine', '.onnx')
        if Path(onnx_path).exists():
            try:
                self._load_onnx(onnx_path)
                self._use_onnx = True
                print(f"[YOLODetector] Loaded ONNX model: {onnx_path}")
                return True
            except Exception as e:
                print(f"[YOLODetector] ONNX load failed: {e}")

        # Fallback to PyTorch (ultralytics)
        try:
            from ultralytics import YOLO
            pt_path = str(model_path).replace('.engine', '.pt').replace('.onnx', '.pt')
            self.model = YOLO(pt_path)
            print(f"[YOLODetector] Loaded PyTorch model: {pt_path}")
            return True
        except Exception as e:
            print(f"[YOLODetector] PyTorch load failed: {e}")
            return False

    def _load_tensorrt(self, engine_path: str):
        """Load TensorRT engine for inference"""
        # In production, use trtexec or TensorRT Python API
        # For now, we use ultralytics YOLO with TensorRT backend
        from ultralytics import YOLO
        self.model = YOLO(engine_path, task='detect')

    def _load_onnx(self, onnx_path: str):
        """Load ONNX model for inference"""
        from ultralytics import YOLO
        self.model = YOLO(onnx_path, task='detect')

    def detect(self, image: np.ndarray) -> List[Detection]:
        """Run detection on a single image

        Args:
            image: BGR image (H, W, 3)

        Returns:
            List of Detection objects
        """
        if self.model is None:
            return []

        t0 = time.time()

        # Run inference
        results = self.model(
            image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        detections = []
        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for i in range(len(boxes)):
                    box = boxes[i]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])

                    cls_name = (
                        self.class_names[cls_id]
                        if cls_id < len(self.class_names)
                        else f"class_{cls_id}"
                    )

                    det = Detection(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=conf,
                        bbox=np.array([x1, y1, x2, y2]),
                        center=np.array([(x1+x2)/2, (y1+y2)/2]),
                        width=float(x2 - x1),
                        height=float(y2 - y1),
                    )
                    detections.append(det)

        # Sort by confidence
        detections.sort(key=lambda d: d.confidence, reverse=True)

        # Limit detections
        if len(detections) > self.max_detections:
            detections = detections[:self.max_detections]

        elapsed = (time.time() - t0) * 1000
        # Log periodically (every 100 frames in production)
        return detections

    def detect_batch(self, images: List[np.ndarray]) -> List[List[Detection]]:
        """Batch detection for multiple images (e.g., visible + IR)"""
        if self.model is None:
            return [[] for _ in images]

        results = self.model(
            images,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        all_detections = []
        for result in results:
            frame_dets = []
            if result.boxes is not None and len(result.boxes) > 0:
                for i in range(len(result.boxes)):
                    box = result.boxes[i]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = (
                        self.class_names[cls_id]
                        if cls_id < len(self.class_names)
                        else f"class_{cls_id}"
                    )
                    frame_dets.append(Detection(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=conf,
                        bbox=np.array([x1, y1, x2, y2]),
                        center=np.array([(x1+x2)/2, (y1+y2)/2]),
                        width=float(x2 - x1),
                        height=float(y2 - y1),
                    ))
            all_detections.append(frame_dets)

        return all_detections

    def draw_detections(self, image: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Draw detection results on image for debugging/display"""
        vis = image.copy()
        for det in detections:
            x1, y1, x2, y2 = det.bbox.astype(int)
            color = self._class_color(det.class_id)
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            label = f"{det.class_name} {det.confidence:.2f}"
            cv2.putText(vis, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return vis

    def _class_color(self, class_id: int) -> tuple:
        """Get color for class visualization"""
        colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 255, 0), (255, 128, 0), (0, 128, 255),
            (128, 0, 255), (255, 255, 128), (128, 128, 128),
        ]
        return colors[class_id % len(colors)]
