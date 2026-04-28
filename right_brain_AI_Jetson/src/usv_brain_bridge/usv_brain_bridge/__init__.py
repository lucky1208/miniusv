"""USV Left-Right Brain Communication Bridge

Responsible for:
- UDP/TCP communication with Right Brain (i.MX8)
- Message serialization/deserialization (JSON + protobuf)
- Command sending (speed, heading, mode)
- State receiving (motor status, BMS, sensor data)
- Heartbeat and watchdog
"""

from .brain_bridge import BrainBridge
from .protocol import (
    BrainMessage, MessageType,
    CommandSpeedHeading, CommandMode,
    StateMotors, StateBMS, StateSensors,
    encode_message, decode_message,
)

__all__ = [
    'BrainBridge', 'BrainMessage', 'MessageType',
    'CommandSpeedHeading', 'CommandMode',
    'StateMotors', 'StateBMS', 'StateSensors',
    'encode_message', 'decode_message',
]
