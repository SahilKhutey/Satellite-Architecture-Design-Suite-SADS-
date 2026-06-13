# SADS - Cowell Propagator (Numerical Integrator)
import numpy as np
from scientific.numerical_methods.solvers import rk45_adaptive_step

class CowellPropagator:
    @staticmethod
    def step(pos: list, vel: list, dt: float, mu: float = 398600.4418) -> tuple:
        """
        Propagate the orbit state by dt seconds using adaptive RK45 integration.
        pos, vel: position (km) and velocity (km/s) vectors
        mu: Earth's gravitational parameter (km^3/s^2)
        """
        y0 = np.array(pos + vel, dtype=float)
        
        def derivatives(t, y):
            r = y[0:3]
            v = y[3:6]
            r_mag = np.linalg.norm(r)
            if r_mag == 0:
                accel = np.zeros(3)
            else:
                accel = -mu * r / (r_mag ** 3)
            return np.concatenate((v, accel))
        
        t = 0.0
        h = dt
        y = y0
        while t < dt:
            h_step = min(h, dt - t)
            y, next_t, h_new = rk45_adaptive_step(derivatives, t, y, h_step)
            if next_t > t:
                t = next_t
            h = h_new
            
        return y[0:3].tolist(), y[3:6].tolist()

