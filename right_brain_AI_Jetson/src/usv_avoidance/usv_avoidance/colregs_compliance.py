"""COLREGs (International Regulations for Preventing Collisions at Sea) Compliance

Implements maritime right-of-way rules:
- Rule 13: Overtaking
- Rule 14: Head-on situation
- Rule 15: Crossing situation
- Rule 17: Action by give-way vessel
- Rule 18: Responsibilities between vessels
"""

import numpy as np
from enum import Enum, auto
from typing import Tuple, Optional
from dataclasses import dataclass


class COLREGsSituation(Enum):
    """COLREGs encounter situation classification"""
    CLEAR = auto()           # No collision risk
    HEAD_ON = auto()         # Rule 14: Head-on
    CROSSING_STARBOARD = auto()  # Rule 15: Crossing, give-way (target on starboard)
    CROSSING_PORT = auto()       # Rule 15: Crossing, stand-on (target on port)
    OVERTAKING = auto()      # Rule 13: Overtaking
    BEING_OVERTAKEN = auto() # Rule 13: Being overtaken
    UNKNOWN = auto()


@dataclass
class EncounterAnalysis:
    """Result of COLREGs encounter analysis"""
    situation: COLREGsSituation
    is_give_way: bool        # True if USV must give way
    cpa_distance: float      # Closest Point of Approach (m)
    cpa_time: float          # Time to CPA (s)
    bearing: float           # Bearing to target (rad)
    relative_heading: float  # Relative heading of target (rad)


class COLREGsCompliance:
    """COLREGs Rule Compliance for USV

    Analyzes encounters with other vessels and determines
    required maneuver according to COLREGs.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self.cpa_threshold = config.get("cpa_threshold", 50.0)   # m - collision risk distance
        self.cpa_time_threshold = config.get("cpa_time_threshold", 60.0)  # s
        self.heading_threshold = config.get("heading_threshold", 0.175)  # ~10° for head-on

    def compute_cpa(self, usv_x: float, usv_y: float,
                    usv_vx: float, usv_vy: float,
                    target_x: float, target_y: float,
                    target_vx: float, target_vy: float) -> Tuple[float, float]:
        """Compute Closest Point of Approach (CPA)

        Returns:
            (cpa_distance, cpa_time)
        """
        # Relative position and velocity
        dx = target_x - usv_x
        dy = target_y - usv_y
        dvx = target_vx - usv_vx
        dvy = target_vy - usv_vy

        # Relative speed squared
        dv2 = dvx*dvx + dvy*dvy

        if dv2 < 1e-6:
            # Nearly stationary relative motion
            return np.sqrt(dx*dx + dy*dy), float('inf')

        # Time to CPA
        t_cpa = -(dx*dvx + dy*dvy) / dv2

        if t_cpa < 0:
            # Moving apart
            return np.sqrt(dx*dx + dy*dy), t_cpa

        # CPA distance
        cpa_x = dx + dvx * t_cpa
        cpa_y = dy + dvy * t_cpa
        cpa_dist = np.sqrt(cpa_x*cpa_x + cpa_y*cpa_y)

        return cpa_dist, t_cpa

    def classify_encounter(self, usv_heading: float,
                           target_bearing: float,
                           target_relative_heading: float,
                           cpa_distance: float,
                           cpa_time: float) -> EncounterAnalysis:
        """Classify encounter situation according to COLREGs

        Args:
            usv_heading: USV heading (rad, from North)
            target_bearing: Bearing to target (rad, from North)
            target_relative_heading: Target's heading relative to USV (rad)
            cpa_distance: CPA distance (m)
            cpa_time: Time to CPA (s)

        Returns:
            EncounterAnalysis with situation and give-way status
        """
        # Check if collision risk exists
        if cpa_distance > self.cpa_threshold or cpa_time < 0 or cpa_time > self.cpa_time_threshold:
            return EncounterAnalysis(
                situation=COLREGsSituation.CLEAR,
                is_give_way=False,
                cpa_distance=cpa_distance,
                cpa_time=cpa_time,
                bearing=target_bearing,
                relative_heading=target_relative_heading,
            )

        # Relative bearing (target bearing relative to USV heading)
        rel_bearing = target_bearing - usv_heading
        rel_bearing = np.arctan2(np.sin(rel_bearing), np.cos(rel_bearing))

        # Head-on situation (Rule 14)
        if abs(rel_bearing) < self.heading_threshold and abs(target_relative_heading - np.pi) < self.heading_threshold * 2:
            return EncounterAnalysis(
                situation=COLREGsSituation.HEAD_ON,
                is_give_way=True,  # Both vessels give way in head-on
                cpa_distance=cpa_distance,
                cpa_time=cpa_time,
                bearing=target_bearing,
                relative_heading=target_relative_heading,
            )

        # Crossing situation (Rule 15)
        # Target on starboard side -> USV gives way
        if 0 < rel_bearing < np.pi:
            return EncounterAnalysis(
                situation=COLREGsSituation.CROSSING_STARBOARD,
                is_give_way=True,
                cpa_distance=cpa_distance,
                cpa_time=cpa_time,
                bearing=target_bearing,
                relative_heading=target_relative_heading,
            )
        else:
            return EncounterAnalysis(
                situation=COLREGsSituation.CROSSING_PORT,
                is_give_way=False,  # Stand-on vessel
                cpa_distance=cpa_distance,
                cpa_time=cpa_time,
                bearing=target_bearing,
                relative_heading=target_relative_heading,
            )

    def get_avoidance_maneuver(self, analysis: EncounterAnalysis,
                                usv_heading: float) -> Tuple[float, float]:
        """Get recommended avoidance maneuver based on COLREGs

        Returns:
            (heading_change, speed_change) - recommended changes
        """
        if analysis.situation == COLREGsSituation.CLEAR:
            return 0.0, 0.0

        if analysis.situation == COLREGsSituation.HEAD_ON:
            # Rule 14: Alter course to starboard
            return -np.radians(30), 0.0  # Turn starboard 30°

        if analysis.situation == COLREGsSituation.CROSSING_STARBOARD:
            # Rule 15: Give-way, alter course to starboard (go behind)
            return -np.radians(30), -2.0  # Turn starboard, reduce speed

        if analysis.situation == COLREGsSituation.OVERTAKING:
            # Rule 13: Give-way, alter course to avoid
            return -np.radians(20), 0.0

        return 0.0, 0.0
