"""USV Left Brain - Automatic Target Recognition (ATR) Module

Responsible for:
- YOLOv8-based maritime target detection
- Target classification (vessel types, buoys, debris, etc.)
- Target tracking (DeepSORT)
- Threat level assessment
"""

from .yolo_detector import YOLODetector
from .target_tracker import TargetTracker
from .atr_pipeline import ATRPipeline

__all__ = ['YOLODetector', 'TargetTracker', 'ATRPipeline']
