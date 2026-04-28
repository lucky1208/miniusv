"""Mission State Machine for USV

Manages high-level mission states:
- IDLE: Waiting for mission
- NAVIGATING: Following waypoints
- AVOIDING: Emergency avoidance maneuver
- PATROLLING: Patrol pattern
- INTERCEPTING: Intercept target
- RETURNING: Return to base
- EMERGENCY: Emergency stop / self-destruct
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable
import time


class MissionState(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    AVOIDING = auto()
    PATROLLING = auto()
    INTERCEPTING = auto()
    RETURNING = auto()
    EMERGENCY = auto()


@dataclass
class MissionContext:
    """Current mission context data"""
    state: MissionState = MissionState.IDLE
    prev_state: MissionState = MissionState.IDLE
    state_enter_time: float = 0.0
    target_id: Optional[int] = None
    mission_id: Optional[str] = None
    reason: str = ""


class MissionStateMachine:
    """USV Mission State Machine

    Manages state transitions with guards and actions.
    """

    # Valid state transitions
    TRANSITIONS = {
        MissionState.IDLE: [MissionState.NAVIGATING, MissionState.PATROLLING, MissionState.EMERGENCY],
        MissionState.NAVIGATING: [MissionState.AVOIDING, MissionState.INTERCEPTING,
                                  MissionState.RETURNING, MissionState.IDLE, MissionState.EMERGENCY],
        MissionState.AVOIDING: [MissionState.NAVIGATING, MissionState.PATROLLING,
                               MissionState.RETURNING, MissionState.EMERGENCY],
        MissionState.PATROLLING: [MissionState.AVOIDING, MissionState.INTERCEPTING,
                                  MissionState.RETURNING, MissionState.IDLE, MissionState.EMERGENCY],
        MissionState.INTERCEPTING: [MissionState.AVOIDING, MissionState.NAVIGATING,
                                    MissionState.RETURNING, MissionState.IDLE, MissionState.EMERGENCY],
        MissionState.RETURNING: [MissionState.AVOIDING, MissionState.IDLE, MissionState.EMERGENCY],
        MissionState.EMERGENCY: [MissionState.IDLE],  # Only manual reset from emergency
    }

    def __init__(self, config: dict = None):
        self.context = MissionContext()
        self._callbacks = {}  # state -> callback function

    def register_callback(self, state: MissionState, callback: Callable):
        """Register callback for state entry"""
        self._callbacks[state] = callback

    def transition(self, new_state: MissionState,
                   target_id: Optional[int] = None,
                   reason: str = "") -> bool:
        """Request state transition

        Args:
            new_state: Target state
            target_id: Optional target ID (for intercept)
            reason: Transition reason

        Returns:
            True if transition allowed and executed
        """
        current = self.context.state

        # Check if transition is valid
        if new_state not in self.TRANSITIONS.get(current, []):
            return False

        # Execute transition
        self.context.prev_state = current
        self.context.state = new_state
        self.context.state_enter_time = time.time()
        self.context.target_id = target_id
        self.context.reason = reason

        # Call state entry callback
        if new_state in self._callbacks:
            self._callbacks[new_state](self.context)

        return True

    def force_state(self, state: MissionState, reason: str = "force"):
        """Force state change (for emergency override)"""
        self.context.prev_state = self.context.state
        self.context.state = state
        self.context.state_enter_time = time.time()
        self.context.reason = reason

    @property
    def state(self) -> MissionState:
        return self.context.state

    @property
    def time_in_state(self) -> float:
        """Seconds in current state"""
        return time.time() - self.context.state_enter_time

    def get_status(self) -> dict:
        """Get mission status as dict"""
        return {
            "state": self.context.state.name,
            "prev_state": self.context.prev_state.name,
            "time_in_state": round(self.time_in_state, 1),
            "target_id": self.context.target_id,
            "mission_id": self.context.mission_id,
            "reason": self.context.reason,
        }
