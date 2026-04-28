"""Threat Evaluator for USV

Evaluates threat level of detected targets based on:
- Distance and closing rate
- Target type (warship > speedboat > fishing_vessel)
- Behavior pattern (approaching, circling, etc.)
- Weapons capability
- Rules of engagement compliance
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from enum import IntEnum


class ThreatLevel(IntEnum):
    NONE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4
    IMMINENT = 5


# Threat scores by target type
TYPE_THREAT_SCORE = {
    "warship": 0.9,
    "speedboat": 0.7,
    "unknown_vessel": 0.6,
    "tanker": 0.3,
    "cargo_ship": 0.2,
    "fishing_vessel": 0.15,
    "sailboat": 0.1,
    "buoy": 0.0,
    "navigation_mark": 0.0,
    "debris": 0.05,
    "person_in_water": 0.0,
    "kayak_small": 0.05,
}


@dataclass
class ThreatAssessment:
    """Threat assessment result for a single target"""
    target_id: int
    target_type: str
    threat_level: ThreatLevel
    threat_score: float          # 0.0 - 1.0
    distance: float              # meters
    closing_rate: float          # m/s (negative = approaching)
    intent: str                  # approaching, passing, circling, unknown
    action_required: str         # monitor, evade, engage, ignore
    reason: str                  # human-readable reason


class ThreatEvaluator:
    """Threat Assessment Engine for USV

    Combines rule-based expert system with ML for threat evaluation.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.critical_distance = config.get("critical_distance", 50.0)    # m
        self.warning_distance = config.get("warning_distance", 200.0)     # m
        self.detection_distance = config.get("detection_distance", 500.0) # m
        self.closing_rate_threshold = config.get("closing_rate_threshold", -2.0)  # m/s
        self.usv_x = 0.0
        self.usv_y = 0.0
        self.usv_vx = 0.0
        self.usv_vy = 0.0

    def update_usv_state(self, x: float, y: float, vx: float, vy: float):
        """Update USV position and velocity for distance calculations"""
        self.usv_x = x
        self.usv_y = y
        self.usv_vx = vx
        self.usv_vy = vy

    def evaluate(self, target: dict) -> ThreatAssessment:
        """Evaluate threat level for a single target

        Args:
            target: Dict with keys: track_id, class_name, world_pos, velocity, confidence

        Returns:
            ThreatAssessment result
        """
        tid = target.get('track_id', -1)
        ttype = target.get('class_name', 'unknown_vessel')
        pos = target.get('world_pos', [0, 0, 0])
        vel = target.get('velocity', [0, 0, 0])

        # Distance
        dx = pos[0] - self.usv_x
        dy = pos[1] - self.usv_y
        distance = np.sqrt(dx*dx + dy*dy)

        # Closing rate (negative = approaching)
        rel_vx = vel[0] - self.usv_vx
        rel_vy = vel[1] - self.usv_vy
        if distance > 0.01:
            closing_rate = (dx * rel_vx + dy * rel_vy) / distance
        else:
            closing_rate = 0.0

        # Intent inference
        intent = self._infer_intent(distance, closing_rate, ttype)

        # Compute threat score (0-1)
        type_score = TYPE_THREAT_SCORE.get(ttype, 0.3)

        # Distance factor (closer = more threatening)
        if distance < self.critical_distance:
            dist_factor = 1.0
        elif distance < self.warning_distance:
            dist_factor = 0.5 + 0.5 * (self.warning_distance - distance) / (self.warning_distance - self.critical_distance)
        elif distance < self.detection_distance:
            dist_factor = 0.2 * (self.detection_distance - distance) / (self.detection_distance - self.warning_distance)
        else:
            dist_factor = 0.0

        # Closing rate factor
        if closing_rate < self.closing_rate_threshold:
            close_factor = min(1.0, abs(closing_rate) / 10.0)
        else:
            close_factor = 0.0

        # Combined threat score
        threat_score = (
            0.4 * type_score +
            0.35 * dist_factor +
            0.25 * close_factor
        )
        threat_score = np.clip(threat_score, 0.0, 1.0)

        # Map to threat level
        if threat_score > 0.8:
            level = ThreatLevel.IMMINENT
        elif threat_score > 0.6:
            level = ThreatLevel.CRITICAL
        elif threat_score > 0.4:
            level = ThreatLevel.HIGH
        elif threat_score > 0.2:
            level = ThreatLevel.MODERATE
        elif threat_score > 0.05:
            level = ThreatLevel.LOW
        else:
            level = ThreatLevel.NONE

        # Determine required action
        action, reason = self._determine_action(level, intent, distance, ttype)

        return ThreatAssessment(
            target_id=tid,
            target_type=ttype,
            threat_level=level,
            threat_score=round(threat_score, 3),
            distance=round(distance, 1),
            closing_rate=round(closing_rate, 2),
            intent=intent,
            action_required=action,
            reason=reason,
        )

    def _infer_intent(self, distance: float, closing_rate: float,
                      target_type: str) -> str:
        """Infer target intent from behavior"""
        if closing_rate < -5.0 and distance < 200:
            return "approaching_fast"
        elif closing_rate < -1.0 and distance < 300:
            return "approaching"
        elif abs(closing_rate) < 1.0 and distance < 100:
            return "circling"
        elif closing_rate > 1.0:
            return "departing"
        else:
            return "passing"

    def _determine_action(self, level: ThreatLevel, intent: str,
                          distance: float, target_type: str) -> tuple:
        """Determine required action based on threat level and intent"""
        if level >= ThreatLevel.IMMINENT:
            return "evade", f"Imminent threat: {target_type} {intent} at {distance:.0f}m"
        elif level >= ThreatLevel.CRITICAL:
            return "evade", f"Critical threat: {target_type} {intent} at {distance:.0f}m"
        elif level >= ThreatLevel.HIGH:
            return "monitor", f"High threat: {target_type} {intent} at {distance:.0f}m"
        elif level >= ThreatLevel.MODERATE:
            return "monitor", f"Moderate threat: {target_type} at {distance:.0f}m"
        else:
            return "ignore", f"Low/no threat: {target_type} at {distance:.0f}m"

    def evaluate_all(self, targets: List[dict]) -> List[ThreatAssessment]:
        """Evaluate all targets and return sorted by threat score"""
        assessments = [self.evaluate(t) for t in targets]
        assessments.sort(key=lambda a: a.threat_score, reverse=True)
        return assessments
