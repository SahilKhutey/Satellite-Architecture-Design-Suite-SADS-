# SADS - Cowell Propagator (Numerical Integrator)
import numpy as np
import math
from scientific.numerical_methods.solvers import rk45_adaptive_step

def get_atmospheric_density(alt_km: float) -> float:
    if alt_km < 100.0:
        return 1.225 * math.exp(-max(0.0, alt_km) / 8.5)
    elif alt_km < 200.0:
        h0, rho0 = 100.0, 5.6e-7
        h1, rho1 = 200.0, 2.5e-10
        H = (h1 - h0) / math.log(rho0 / rho1)
        return rho0 * math.exp(-(alt_km - h0) / H)
    elif alt_km < 400.0:
        h0, rho0 = 200.0, 2.5e-10
        h1, rho1 = 400.0, 2.8e-12
        H = (h1 - h0) / math.log(rho0 / rho1)
        return rho0 * math.exp(-(alt_km - h0) / H)
    elif alt_km < 800.0:
        h0, rho0 = 400.0, 2.8e-12
        h1, rho1 = 800.0, 1.0e-14
        H = (h1 - h0) / math.log(rho0 / rho1)
        return rho0 * math.exp(-(alt_km - h0) / H)
    else:
        return 0.0

class CowellPropagator:
    @staticmethod
    def step(
        pos: list, 
        vel: list, 
        dt: float, 
        mu: float = 398600.4418, 
        mass: float = 150.0, 
        area: float = 2.0, 
        cd: float = 2.2, 
        use_perturbations: bool = True
    ) -> tuple:
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
                if use_perturbations:
                    # 1. J2 Perturbation
                    z = r[2]
                    z2_r2 = (z / r_mag) ** 2
                    factor = -1.5 * 1.08263e-3 * mu * (6378.137 ** 2) / (r_mag ** 5)
                    a_j2 = factor * np.array([
                        (1.0 - 5.0 * z2_r2) * r[0],
                        (1.0 - 5.0 * z2_r2) * r[1],
                        (3.0 - 5.0 * z2_r2) * r[2]
                    ])
                    accel = accel + a_j2
                    
                    # 2. Atmospheric Drag (if below 800 km)
                    alt_km = r_mag - 6378.137
                    if alt_km < 800.0:
                        rho = get_atmospheric_density(alt_km)
                        omega_e = 7.292115e-5
                        v_rel = np.array([
                            v[0] + omega_e * r[1],
                            v[1] - omega_e * r[0],
                            v[2]
                        ])
                        v_rel_mag = np.linalg.norm(v_rel)
                        if v_rel_mag > 0:
                            a_drag = -0.5 * rho * 1000.0 * (cd * area / mass) * v_rel_mag * v_rel
                            accel = accel + a_drag
                            
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
