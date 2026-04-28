"""USV Left Brain - Obstacle Avoidance Module

Responsible for:
- DWA (Dynamic Window Approach) local avoidance
- Artificial Potential Field method
- COLREGs-compliant maneuver selection
"""

from .dwa_avoidance import DWAAvoidance
from .potential_field import PotentialFieldAvoidance
from .colregs_compliance import COLREGsCompliance

__all__ = ['DWAAvoidance', 'PotentialFieldAvoidance', 'COLREGsCompliance']
