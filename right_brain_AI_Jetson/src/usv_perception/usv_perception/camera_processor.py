"""Camera Processor for USV

Handles dual-light (visible + IR) camera system:
- Image acquisition from GStreamer pipeline
- Image preprocessing (undistort, resize, normalize)
- Visual + IR image fusion
- Frame synchronization
"""

import numpy as np
import cv2
from typing import Optional, Tuple
import threading
import time


class CameraProcessor:
    """Dual-Light Camera Processor

    Specs (from design doc):
    - Visible: 1920×1080, 30x optical zoom
    - IR: 640×512, uncooled
    - FOV: 60°(wide) ~ 2°(narrow)
    - Stabilization: 50μrad
    - Target ID range: 5km (vessel)
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.visible_width = config.get("visible_width", 1920)
        self.visible_height = config.get("visible_height", 1080)
        self.ir_width = config.get("ir_width", 640)
        self.ir_height = config.get("ir_height", 512)
        self.fps = config.get("fps", 30)
        self.enable_ir = config.get("enable_ir", True)

        # Camera calibration (loaded from file in production)
        self.visible_K = np.eye(3)  # intrinsic matrix
        self.visible_dist = np.zeros(5)  # distortion coefficients
        self.ir_K = np.eye(3)
        self.ir_dist = np.zeros(5)

        # Frame buffers
        self._visible_frame: Optional[np.ndarray] = None
        self._ir_frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False

        # GStreamer pipelines
        self.visible_pipeline = self._build_visible_pipeline()
        self.ir_pipeline = self._build_ir_pipeline() if self.enable_ir else None

    def _build_visible_pipeline(self) -> str:
        """Build GStreamer pipeline for visible light camera (Jetson MIPI CSI)"""
        return (
            f"nvarguscamerasrc sensor-id=0 ! "
            f"video/x-raw(memory:NVMM), width={self.visible_width}, "
            f"height={self.visible_height}, framerate={self.fps}/1 ! "
            f"nvvidconv ! video/x-raw, format=BGR ! "
            f"appsink drop=true sync=false max-buffers=2"
        )

    def _build_ir_pipeline(self) -> str:
        """Build GStreamer pipeline for IR camera (USB/RTSP)"""
        return (
            f"v4l2src device=/dev/video1 ! "
            f"video/x-raw, width={self.ir_width}, height={self.ir_height}, "
            f"framerate={self.fps}/1 ! "
            f"videoconvert ! video/x-raw, format=BGR ! "
            f"appsink drop=true sync=false max-buffers=2"
        )

    def start(self) -> bool:
        """Start camera capture pipelines"""
        try:
            self.visible_cap = cv2.VideoCapture(self.visible_pipeline, cv2.CAP_GSTREAMER)
            if not self.visible_cap.isOpened():
                # Fallback to default camera for development
                self.visible_cap = cv2.VideoCapture(0)

            if self.enable_ir and self.ir_pipeline:
                self.ir_cap = cv2.VideoCapture(self.ir_pipeline, cv2.CAP_GSTREAMER)
                if not self.ir_cap.isOpened():
                    self.ir_cap = cv2.VideoCapture(1)

            self._running = True
            return True
        except Exception as e:
            print(f"[CameraProcessor] Start failed: {e}")
            return False

    def stop(self):
        """Stop camera capture"""
        self._running = False
        if hasattr(self, 'visible_cap') and self.visible_cap:
            self.visible_cap.release()
        if hasattr(self, 'ir_cap') and self.ir_cap:
            self.ir_cap.release()

    def get_frames(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Get latest synchronized frames

        Returns:
            (visible_frame, ir_frame) tuple
        """
        visible_frame = None
        ir_frame = None

        if hasattr(self, 'visible_cap') and self.visible_cap.isOpened():
            ret, visible_frame = self.visible_cap.read()
            if ret and visible_frame is not None:
                visible_frame = self.preprocess_visible(visible_frame)

        if self.enable_ir and hasattr(self, 'ir_cap') and self.ir_cap.isOpened():
            ret, ir_frame = self.ir_cap.read()
            if ret and ir_frame is not None:
                ir_frame = self.preprocess_ir(ir_frame)

        with self._lock:
            self._visible_frame = visible_frame
            self._ir_frame = ir_frame

        return visible_frame, ir_frame

    def preprocess_visible(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess visible light image: undistort + resize for AI model"""
        # Undistort using calibration
        h, w = frame.shape[:2]
        new_K, roi = cv2.getOptimalNewCameraMatrix(
            self.visible_K, self.visible_dist, (w, h), 1, (w, h)
        )
        undistorted = cv2.undistort(
            frame, self.visible_K, self.visible_dist, None, new_K
        )

        # Resize to model input size (640x480 for YOLO)
        resized = cv2.resize(undistorted, (640, 480))
        return resized

    def preprocess_ir(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess IR image: normalize + colormap + resize"""
        # Normalize to 0-255
        if frame.dtype != np.uint8:
            normalized = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        else:
            normalized = frame

        # Apply colormap for visualization (WHITEHOT style)
        colored = cv2.applyColorMap(normalized, cv2.COLORMAP_BONE)

        # Resize to match visible
        resized = cv2.resize(colored, (640, 480))
        return resized

    def fuse_visible_ir(self, visible: np.ndarray, ir: np.ndarray,
                        alpha: float = 0.6) -> np.ndarray:
        """Fuse visible and IR images for enhanced detection

        Args:
            visible: Visible light image (BGR)
            ir: IR image (BGR, already colormapped)
            alpha: Blending weight for visible (1-alpha for IR)

        Returns:
            Fused image
        """
        if visible is None:
            return ir
        if ir is None:
            return visible

        # Ensure same size
        if visible.shape != ir.shape:
            ir = cv2.resize(ir, (visible.shape[1], visible.shape[0]))

        fused = cv2.addWeighted(visible, alpha, ir, 1.0 - alpha, 0)
        return fused
