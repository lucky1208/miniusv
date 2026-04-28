"""Brain Bridge - Communication Manager between Left and Right Brain

Manages UDP/TCP sockets for real-time communication between
Jetson Orin NX (Left Brain) and i.MX8 (Right Brain).
"""

import socket
import threading
import time
import queue
from typing import Optional, Callable, Dict
from .protocol import (
    MessageType, BrainMessage,
    encode_message, decode_message,
    CommandSpeedHeading, StateMotors, StateBMS, StateSensors,
)


class BrainBridge:
    """Left-Right Brain Communication Bridge

    Left Brain (Jetson Orin NX) <-> Right Brain (i.MX8)
    via Ethernet (GbE)

    - UDP port 9876: Real-time control commands & status (50Hz)
    - TCP port 9877: Reliable commands (mode change, config)
    """

    UDP_PORT = 9876
    TCP_PORT = 9877
    BUFFER_SIZE = 4096
    HEARTBEAT_INTERVAL = 0.5  # seconds
    RECEIVE_TIMEOUT = 0.02    # seconds

    def __init__(self, right_brain_ip: str = "192.168.1.100",
                 config: dict = None):
        config = config or {}
        self.right_brain_ip = right_brain_ip
        self.left_brain_ip = config.get("left_brain_ip", "192.168.1.1")

        # Sequence counter
        self._seq = 0

        # Received state from Right Brain
        self.motor_state: Optional[StateMotors] = None
        self.bms_state: Optional[StateBMS] = None
        self.sensor_state: Optional[StateSensors] = None

        # Send queue
        self._send_queue = queue.Queue(maxsize=100)

        # Callbacks for received messages
        self._callbacks: Dict[MessageType, Callable] = {}

        # Threading
        self._running = False
        self._udp_sock: Optional[socket.socket] = None
        self._tcp_sock: Optional[socket.socket] = None
        self._recv_thread: Optional[threading.Thread] = None
        self._send_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None

        # Connection state
        self.connected = False
        self.last_heartbeat_time = 0.0
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start communication bridge"""
        try:
            # UDP socket for real-time data
            self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._udp_sock.bind(("0.0.0.0", self.UDP_PORT))
            self._udp_sock.settimeout(self.RECEIVE_TIMEOUT)

            self._running = True

            # Start receive thread
            self._recv_thread = threading.Thread(
                target=self._receive_loop, daemon=True
            )
            self._recv_thread.start()

            # Start send thread
            self._send_thread = threading.Thread(
                target=self._send_loop, daemon=True
            )
            self._send_thread.start()

            # Start heartbeat thread
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop, daemon=True
            )
            self._heartbeat_thread.start()

            print(f"[BrainBridge] Started - Right Brain at {self.right_brain_ip}")
            return True

        except Exception as e:
            print(f"[BrainBridge] Start failed: {e}")
            return False

    def stop(self):
        """Stop communication bridge"""
        self._running = False

        if self._udp_sock:
            self._udp_sock.close()
        if self._tcp_sock:
            self._tcp_sock.close()

        print("[BrainBridge] Stopped")

    def send_speed_heading(self, speed: float, heading: float,
                           yaw_rate: float = 0.0, mode: str = "auto"):
        """Send speed and heading command to Right Brain

        Args:
            speed: Target speed (m/s)
            heading: Target heading (rad)
            yaw_rate: Target yaw rate (rad/s)
            mode: Control mode
        """
        cmd = CommandSpeedHeading(
            speed=speed, heading=heading,
            yaw_rate=yaw_rate, mode=mode
        )
        payload = {
            "speed": speed,
            "heading": heading,
            "yaw_rate": yaw_rate,
            "mode": mode,
        }
        self._enqueue_message(MessageType.COMMAND_SPEED_HEADING, payload)

    def send_mode(self, mode: str, params: dict = None):
        """Send mode change command"""
        payload = {"mode": mode, "params": params or {}}
        self._enqueue_message(MessageType.COMMAND_MODE, payload)

    def send_emergency_stop(self):
        """Send emergency stop command"""
        self._enqueue_message(MessageType.COMMAND_EMERGENCY_STOP, {})

    def register_callback(self, msg_type: MessageType, callback: Callable):
        """Register callback for specific message type"""
        self._callbacks[msg_type] = callback

    def _enqueue_message(self, msg_type: MessageType, payload: dict):
        """Enqueue message for sending"""
        try:
            self._send_queue.put_nowait((msg_type, payload))
        except queue.Full:
            pass  # Drop oldest if queue full

    def _receive_loop(self):
        """UDP receive loop (runs in thread)"""
        while self._running:
            try:
                data, addr = self._udp_sock.recvfrom(self.BUFFER_SIZE)
                msg = decode_message(data)
                if msg is None:
                    continue

                self._handle_message(msg)

            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    pass  # Log in production

    def _send_loop(self):
        """UDP send loop (runs in thread)"""
        while self._running:
            try:
                msg_type, payload = self._send_queue.get(timeout=0.01)

                self._seq += 1
                data = encode_message(msg_type, payload, self._seq)

                self._udp_sock.sendto(
                    data, (self.right_brain_ip, self.UDP_PORT)
                )

            except queue.Empty:
                continue
            except Exception as e:
                if self._running:
                    pass

    def _heartbeat_loop(self):
        """Heartbeat loop (runs in thread)"""
        while self._running:
            self._enqueue_message(MessageType.HEARTBEAT, {
                "source": "left_brain",
                "status": "ok",
            })
            time.sleep(self.HEARTBEAT_INTERVAL)

    def _handle_message(self, msg: BrainMessage):
        """Handle received message from Right Brain"""
        with self._lock:
            if msg.msg_type == MessageType.HEARTBEAT:
                self.connected = True
                self.last_heartbeat_time = time.time()

            elif msg.msg_type == MessageType.STATE_MOTORS:
                p = msg.payload
                self.motor_state = StateMotors(
                    left_rpm=p.get('left_rpm', 0),
                    right_rpm=p.get('right_rpm', 0),
                    left_current=p.get('left_current', 0),
                    right_current=p.get('right_current', 0),
                    left_temp=p.get('left_temp', 0),
                    right_temp=p.get('right_temp', 0),
                    left_fault=p.get('left_fault', 0),
                    right_fault=p.get('right_fault', 0),
                )

            elif msg.msg_type == MessageType.STATE_BMS:
                p = msg.payload
                self.bms_state = StateBMS(
                    voltage=p.get('voltage', 0),
                    current=p.get('current', 0),
                    soc=p.get('soc', 0),
                    soh=p.get('soh', 0),
                    max_cell_temp=p.get('max_cell_temp', 0),
                    min_cell_voltage=p.get('min_cell_voltage', 0),
                    max_cell_voltage=p.get('max_cell_voltage', 0),
                    fault_code=p.get('fault_code', 0),
                    remaining_range=p.get('remaining_range', 0),
                )

            elif msg.msg_type == MessageType.STATE_SENSORS:
                p = msg.payload
                self.sensor_state = StateSensors(
                    gps_lat=p.get('gps_lat', 0),
                    gps_lon=p.get('gps_lon', 0),
                    gps_alt=p.get('gps_alt', 0),
                    gps_accuracy=p.get('gps_accuracy', 0),
                    ins_roll=p.get('ins_roll', 0),
                    ins_pitch=p.get('ins_pitch', 0),
                    ins_yaw=p.get('ins_yaw', 0),
                    ins_wx=p.get('ins_wx', 0),
                    ins_wy=p.get('ins_wy', 0),
                    ins_wz=p.get('ins_wz', 0),
                    water_temp=p.get('water_temp', 0),
                    water_depth=p.get('water_depth', 0),
                )

        # Call registered callback
        if msg.msg_type in self._callbacks:
            self._callbacks[msg.msg_type](msg)

    def get_status(self) -> dict:
        """Get bridge status"""
        return {
            "connected": self.connected,
            "right_brain_ip": self.right_brain_ip,
            "last_heartbeat": round(time.time() - self.last_heartbeat_time, 2),
            "seq": self._seq,
            "queue_size": self._send_queue.qsize(),
        }
