import numpy as np
from scientific.state_estimation.ekf_estimator import ExtendedKalmanFilter

class EKFEstimator:
    def __init__(self, state_dim: int = 2, measurement_dim: int = 1):
        x0 = np.zeros(state_dim)
        P0 = np.eye(state_dim) * 0.1
        Q = np.eye(state_dim) * 0.01
        R = np.eye(measurement_dim) * 0.1
        self.ekf = ExtendedKalmanFilter(x0, P0, Q, R)

    def step(self, state: list, measurement: list) -> list:
        # The transition matrix is assumed identity for simple updates
        def f(x):
            return np.array(state)
        
        def F_jac(x):
            return np.eye(len(x))
            
        self.ekf.predict(f, F_jac)
        
        n_meas = len(measurement)
        n_state = len(state)
        
        def h(x):
            h_val = np.zeros(n_meas)
            for i in range(min(n_meas, n_state)):
                h_val[i] = x[i]
            return h_val
            
        def H_jac(x):
            H = np.zeros((n_meas, n_state))
            for i in range(min(n_meas, n_state)):
                H[i, i] = 1.0
            return H
            
        updated_x = self.ekf.update(np.array(measurement), h, H_jac)
        return updated_x.tolist()

