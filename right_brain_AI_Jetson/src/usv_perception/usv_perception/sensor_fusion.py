"""Extended Kalman Filter (EKF) Multi-Sensor Fusion

Fuses data from:
- GPS/RTK (position)
- MEMS INS (attitude, angular rates)
- LiDAR (obstacle positions)
- mmWave Radar (target positions and velocities)
- Camera (visual bearing)

Implements EKF for USV state estimation:
State vector: [x, y, z, vx, vy, vz, roll, pitch, yaw, wx, wy, wz]
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class USVState:
    """USV navigation state"""
    x: float = 0.0          # position x (m) - East
    y: float = 0.0          # position y (m) - North
    z: float = 0.0          # position z (m) - Up
    vx: float = 0.0         # velocity x (m/s)
    vy: float = 0.0         # velocity y (m/s)
    vz: float = 0.0         # velocity z (m/s)
    roll: float = 0.0       # roll (rad)
    pitch: float = 0.0      # pitch (rad)
    yaw: float = 0.0        # yaw/heading (rad)
    wx: float = 0.0         # angular velocity roll (rad/s)
    wy: float = 0.0         # angular velocity pitch (rad/s)
    wz: float = 0.0         # angular velocity yaw (rad/s)

    def to_array(self) -> np.ndarray:
        return np.array([
            self.x, self.y, self.z,
            self.vx, self.vy, self.vz,
            self.roll, self.pitch, self.yaw,
            self.wx, self.wy, self.wz
        ])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'USVState':
        return cls(**{
            name: float(arr[i])
            for i, name in enumerate([
                'x', 'y', 'z', 'vx', 'vy', 'vz',
                'roll', 'pitch', 'yaw', 'wx', 'wy', 'wz'
            ])
        })


class SensorFusionEKF:
    """Extended Kalman Filter for USV State Estimation

    State: [x, y, z, vx, vy, vz, roll, pitch, yaw, wx, wy, wz] (12-dim)
    """

    STATE_DIM = 12

    def __init__(self, config: dict = None):
        config = config or {}

        # State and covariance
        self.state = USVState()
        self.x = np.zeros(self.STATE_DIM)
        self.P = np.eye(self.STATE_DIM) * config.get("init_cov", 10.0)

        # Process noise
        q_pos = config.get("q_pos", 0.1)       # position process noise
        q_vel = config.get("q_vel", 0.5)       # velocity process noise
        q_att = config.get("q_att", 0.01)      # attitude process noise
        q_gyro = config.get("q_gyro", 0.1)     # gyro process noise
        self.Q = np.diag([
            q_pos, q_pos, q_pos,
            q_vel, q_vel, q_vel,
            q_att, q_att, q_att,
            q_gyro, q_gyro, q_gyro
        ])

        # GPS measurement noise
        r_gps = config.get("r_gps", 2.0)
        self.R_gps = np.diag([r_gps, r_gps, r_gps])

        # INS measurement noise
        r_att = config.get("r_att", 0.005)
        r_gyro = config.get("r_gyro", 0.01)
        self.R_ins = np.diag([r_att, r_att, r_att, r_gyro, r_gyro, r_gyro])

        # Velocity measurement noise (from radar/DVL)
        r_vel = config.get("r_vel", 0.1)
        self.R_vel = np.diag([r_vel, r_vel, r_vel])

        self.initialized = False

    def predict(self, dt: float, imu_data: Optional[dict] = None):
        """EKF prediction step using constant-velocity model + IMU

        Args:
            dt: Time step (s)
            imu_data: Optional IMU data dict with 'ax','ay','az','wx','wy','wz'
        """
        x = self.x

        # State transition (constant velocity + rotation)
        F = np.eye(self.STATE_DIM)
        F[0, 3] = dt   # x += vx * dt
        F[1, 4] = dt   # y += vy * dt
        F[2, 5] = dt   # z += vz * dt
        F[6, 9] = dt   # roll += wx * dt
        F[7, 10] = dt  # pitch += wy * dt
        F[8, 11] = dt  # yaw += wz * dt

        # If IMU data available, use it for acceleration
        if imu_data:
            ax = imu_data.get('ax', 0.0)
            ay = imu_data.get('ay', 0.0)
            az = imu_data.get('az', -9.81)

            # Rotate acceleration from body to world frame
            roll, pitch, yaw = x[6], x[7], x[8]
            cr, sr = np.cos(roll), np.sin(roll)
            cp, sp = np.cos(pitch), np.sin(pitch)
            cy, sy = np.cos(yaw), np.sin(yaw)

            # Simplified rotation (body -> world)
            ax_w = (cy*cp)*ax + (cy*sp*sr - sy*cr)*ay + (cy*sp*cr + sy*sr)*az
            ay_w = (sy*cp)*ax + (sy*sp*sr + cy*cr)*ay + (sy*sp*cr - cy*sr)*az

            # Update velocity with acceleration
            x[3] += ax_w * dt
            x[4] += ay_w * dt

            # Update angular rates from gyro
            x[9] = imu_data.get('wx', x[9])
            x[10] = imu_data.get('wy', x[10])
            x[11] = imu_data.get('wz', x[11])

        # Predict state
        self.x = F @ x

        # Predict covariance
        self.P = F @ self.P @ F.T + self.Q * dt

        # Update state object
        self.state = USVState.from_array(self.x)

    def update_gps(self, lat: float, lon: float, alt: float = 0.0,
                   accuracy: float = 2.0):
        """EKF update with GPS/RTK measurement

        Args:
            lat, lon: Position in local frame (meters from origin)
            alt: Altitude (m)
            accuracy: GPS accuracy estimate (m)
        """
        if not self.initialized:
            self.x[0] = lat
            self.x[1] = lon
            self.x[2] = alt
            self.initialized = True
            return

        # Measurement model: z = H @ x
        H = np.zeros((3, self.STATE_DIM))
        H[0, 0] = 1.0  # x
        H[1, 1] = 1.0  # y
        H[2, 2] = 1.0  # z

        z = np.array([lat, lon, alt])
        z_pred = H @ self.x
        innovation = z - z_pred

        # Adaptive R based on accuracy
        R = np.diag([accuracy**2, accuracy**2, (accuracy*2)**2])

        # Kalman gain
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update
        self.x = self.x + K @ innovation
        self.P = (np.eye(self.STATE_DIM) - K @ H) @ self.P
        self.state = USVState.from_array(self.x)

    def update_ins(self, roll: float, pitch: float, yaw: float,
                   wx: float, wy: float, wz: float):
        """EKF update with INS attitude measurement

        Args:
            roll, pitch, yaw: Attitude angles (rad)
            wx, wy, wz: Angular rates (rad/s)
        """
        H = np.zeros((6, self.STATE_DIM))
        H[0, 6] = 1.0   # roll
        H[1, 7] = 1.0   # pitch
        H[2, 8] = 1.0   # yaw
        H[3, 9] = 1.0   # wx
        H[4, 10] = 1.0  # wy
        H[5, 11] = 1.0  # wz

        z = np.array([roll, pitch, yaw, wx, wy, wz])
        z_pred = H @ self.x
        innovation = z - z_pred

        # Wrap yaw angle
        innovation[2] = np.arctan2(np.sin(innovation[2]), np.cos(innovation[2]))

        S = H @ self.P @ H.T + self.R_ins
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ innovation
        self.P = (np.eye(self.STATE_DIM) - K @ H) @ self.P
        self.state = USVState.from_array(self.x)

    def update_velocity(self, vx: float, vy: float, vz: float = 0.0):
        """EKF update with velocity measurement (from radar/DVL)"""
        H = np.zeros((3, self.STATE_DIM))
        H[0, 3] = 1.0  # vx
        H[1, 4] = 1.0  # vy
        H[2, 5] = 1.0  # vz

        z = np.array([vx, vy, vz])
        innovation = z - H @ self.x

        S = H @ self.P @ H.T + self.R_vel
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ innovation
        self.P = (np.eye(self.STATE_DIM) - K @ H) @ self.P
        self.state = USVState.from_array(self.x)

    def get_state(self) -> USVState:
        """Get current estimated state"""
        return self.state

    def get_state_dict(self) -> dict:
        """Get state as dict for inter-brain communication"""
        return {
            "x": round(self.state.x, 3),
            "y": round(self.state.y, 3),
            "z": round(self.state.z, 3),
            "vx": round(self.state.vx, 3),
            "vy": round(self.state.vy, 3),
            "vz": round(self.state.vz, 3),
            "roll": round(np.degrees(self.state.roll), 2),
            "pitch": round(np.degrees(self.state.pitch), 2),
            "yaw": round(np.degrees(self.state.yaw), 2),
            "speed": round(np.sqrt(self.state.vx**2 + self.state.vy**2), 2),
            "heading": round(np.degrees(self.state.yaw), 2),
        }
