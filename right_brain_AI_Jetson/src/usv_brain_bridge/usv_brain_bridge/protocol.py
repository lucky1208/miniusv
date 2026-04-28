"""Left-Right Brain Communication Protocol

Defines message types and serialization for communication between
Left Brain (Jetson Orin NX) and Right Brain (i.MX8) via Ethernet.

Protocol:
- Transport: UDP (low latency) + TCP (reliable commands)
- Port: 9876 (UDP), 9877 (TCP)
- Format: JSON with CRC16 checksum
- Frequency: 50Hz control loop, 10Hz status

Message structure:
{
    "msg_type": "COMMAND_SPEED_HEADING",
    "timestamp": 1234567890.123,
    "seq": 42,
    "payload": { ... },
    "crc16": 0xABCD
}
"""

import json
import struct
import time
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


class MessageType(Enum):
    # Commands (Left -> Right)
    COMMAND_SPEED_HEADING = auto()   # Set speed and heading
    COMMAND_MODE = auto()            # Set operating mode
    COMMAND_EMERGENCY_STOP = auto()  # Emergency stop
    COMMAND_WAYPOINT = auto()        # Set next waypoint
    COMMAND_MOTOR_DIRECT = auto()    # Direct motor control (debug)

    # Status (Right -> Left)
    STATE_MOTORS = auto()            # Motor status
    STATE_BMS = auto()               # Battery status
    STATE_SENSORS = auto()           # Raw sensor data
    STATE_NAV = auto()               # Navigation state
    STATE_HEALTH = auto()            # System health

    # Bidirectional
    HEARTBEAT = auto()               # Keepalive
    ACK = auto()                     # Acknowledgment


@dataclass
class CommandSpeedHeading:
    """Speed and heading command from Left Brain to Right Brain"""
    speed: float          # m/s (positive forward)
    heading: float        # rad (from North, clockwise)
    yaw_rate: float = 0.0  # rad/s (optional direct yaw rate)
    mode: str = "auto"    # auto, manual, emergency


@dataclass
class CommandMode:
    """Operating mode command"""
    mode: str             # idle, patrol, intercept, return, emergency
    params: Dict = None   # mode-specific parameters


@dataclass
class StateMotors:
    """Motor status from Right Brain"""
    left_rpm: float
    right_rpm: float
    left_current: float   # Amps
    right_current: float
    left_temp: float      # Celsius
    right_temp: float
    left_fault: int       # fault code (0=OK)
    right_fault: int


@dataclass
class StateBMS:
    """Battery Management System status from Right Brain"""
    voltage: float        # Total pack voltage (V)
    current: float        # Pack current (A)
    soc: float            # State of charge (0-100%)
    soh: float            # State of health (0-100%)
    max_cell_temp: float  # Max cell temperature (C)
    min_cell_voltage: float  # Min cell voltage (V)
    max_cell_voltage: float  # Max cell voltage (V)
    fault_code: int       # 0=OK
    remaining_range: float  # Estimated range (m)


@dataclass
class StateSensors:
    """Raw sensor data from Right Brain"""
    gps_lat: float        # degrees
    gps_lon: float        # degrees
    gps_alt: float        # m
    gps_accuracy: float   # m
    ins_roll: float       # rad
    ins_pitch: float      # rad
    ins_yaw: float        # rad
    ins_wx: float         # rad/s
    ins_wy: float
    ins_wz: float
    water_temp: float     # Celsius
    water_depth: float    # m (from sonar)


@dataclass
class BrainMessage:
    """Generic brain-to-brain message"""
    msg_type: MessageType
    timestamp: float
    seq: int
    payload: Dict[str, Any]
    crc16: int = 0


def _crc16(data: bytes) -> int:
    """CRC16-CCITT checksum"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def encode_message(msg_type: MessageType, payload: Dict[str, Any],
                   seq: int = 0) -> bytes:
    """Encode a message to bytes for transmission

    Args:
        msg_type: Message type
        payload: Message payload dict
        seq: Sequence number

    Returns:
        JSON-encoded bytes with CRC
    """
    msg = {
        "msg_type": msg_type.name,
        "timestamp": time.time(),
        "seq": seq,
        "payload": payload,
        "crc16": 0,
    }

    # Compute CRC on payload
    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
    msg["crc16"] = _crc16(payload_bytes)

    return json.dumps(msg).encode('utf-8')


def decode_message(data: bytes) -> Optional[BrainMessage]:
    """Decode received bytes to BrainMessage

    Args:
        data: Received bytes

    Returns:
        BrainMessage or None if invalid
    """
    try:
        msg = json.loads(data.decode('utf-8'))

        msg_type = MessageType[msg["msg_type"]]
        timestamp = msg["timestamp"]
        seq = msg["seq"]
        payload = msg["payload"]
        received_crc = msg.get("crc16", 0)

        # Verify CRC
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        computed_crc = _crc16(payload_bytes)

        if received_crc != computed_crc:
            return None  # CRC mismatch

        return BrainMessage(
            msg_type=msg_type,
            timestamp=timestamp,
            seq=seq,
            payload=payload,
            crc16=received_crc,
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return None
