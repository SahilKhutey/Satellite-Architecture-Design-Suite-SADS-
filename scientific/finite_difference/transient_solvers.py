# SADS Scientific - Finite Difference Solvers
import numpy as np

class HeatEquation1DSolver:
    @staticmethod
    def solve_transient(
        length_m: float, 
        thermal_diffusivity: float, 
        init_temp_k: float, 
        boundary_temps_k: tuple, 
        nodes: int = 10, 
        time_steps: int = 50, 
        dt: float = 0.1
    ) -> np.ndarray:
        dx = length_m / (nodes - 1)
        
        # Stability check
        fourier_no = thermal_diffusivity * dt / (dx ** 2)
        if fourier_no > 0.5:
            dt = 0.45 * (dx ** 2) / thermal_diffusivity
            fourier_no = 0.45
            
        u = np.ones(nodes) * init_temp_k
        u[0] = boundary_temps_k[0]
        u[-1] = boundary_temps_k[1]
        
        history = [u.copy()]
        for _ in range(time_steps):
            u_next = u.copy()
            for i in range(1, nodes - 1):
                u_next[i] = u[i] + fourier_no * (u[i+1] - 2.0*u[i] + u[i-1])
            u = u_next
            history.append(u.copy())
            
        return np.array(history)
