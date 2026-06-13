# SADS Scientific - General Extended Kalman Filter (EKF)
import numpy as np
from typing import Callable

class ExtendedKalmanFilter:
    def __init__(self, x0: np.ndarray, P0: np.ndarray, Q: np.ndarray, R: np.ndarray):
        """
        x0: Initial state vector of shape (n,)
        P0: Initial state covariance matrix of shape (n, n)
        Q: Process noise covariance matrix of shape (n, n)
        R: Measurement noise covariance matrix of shape (m, m)
        """
        self.x = np.array(x0, dtype=float)
        self.P = np.array(P0, dtype=float)
        self.Q = np.array(Q, dtype=float)
        self.R = np.array(R, dtype=float)
        self.n = len(x0)

    def predict(self, f: Callable[[np.ndarray], np.ndarray], F_jacobian: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        """
        f: State transition function x_{k} = f(x_{k-1})
        F_jacobian: Jacobian matrix of f with respect to x (shape: n x n)
        """
        self.x = f(self.x)
        F = F_jacobian(self.x)
        self.P = F @ self.P @ F.T + self.Q
        return self.x

    def update(self, z: np.ndarray, h: Callable[[np.ndarray], np.ndarray], H_jacobian: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        """
        z: Measurement vector of shape (m,)
        h: Measurement function z = h(x)
        H_jacobian: Jacobian matrix of h with respect to x (shape: m x n)
        """
        z_pred = h(self.x)
        y = z - z_pred
        H = H_jacobian(self.x)
        
        S = H @ self.P @ H.T + self.R
        try:
            K = self.P @ H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S_reg = S + np.eye(len(S)) * 1e-9
            K = self.P @ H.T @ np.linalg.inv(S_reg)
            
        self.x = self.x + K @ y
        I = np.eye(self.n)
        self.P = (I - K @ H) @ self.P
        return self.x
