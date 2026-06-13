# SADS Scientific - Numerical Solvers
import numpy as np
from typing import Callable, Tuple

def rk4_step(f: Callable[[float, np.ndarray], np.ndarray], t: float, y: np.ndarray, h: float) -> np.ndarray:
    k1 = f(t, y)
    k2 = f(t + h/2.0, y + h * k1 / 2.0)
    k3 = f(t + h/2.0, y + h * k2 / 2.0)
    k4 = f(t + h, y + h * k3)
    return y + (h / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)

def rk45_adaptive_step(
    f: Callable[[float, np.ndarray], np.ndarray], 
    t: float, 
    y: np.ndarray, 
    h: float, 
    tol: float = 1e-6
) -> Tuple[np.ndarray, float, float]:
    k1 = h * f(t, y)
    k2 = h * f(t + h/4.0, y + k1/4.0)
    k3 = h * f(t + 3.0*h/8.0, y + 3.0*k1/32.0 + 9.0*k2/32.0)
    k4 = h * f(t + 12.0*h/13.0, y + 1932.0*k1/2197.0 - 7200.0*k2/2197.0 + 7296.0*k3/2197.0)
    k5 = h * f(t + h, y + 439.0*k1/216.0 - 8.0*k2 + 3680.0*k3/513.0 - 845.0*k4/4104.0)
    k6 = h * f(t + h/2.0, y - 8.0*k1/27.0 + 2.0*k2 - 3544.0*k3/2565.0 + 1859.0*k4/4104.0 - 11.0*k5/40.0)

    y_4 = y + 25.0*k1/216.0 + 1408.0*k3/2565.0 + 2197.0*k4/4104.0 - k5/5.0
    y_5 = y + 16.0*k1/135.0 + 6656.0*k3/12825.0 + 28561.0*k4/56430.0 - 9.0*k5/50.0 + 2.0*k6/55.0
    
    error = np.linalg.norm(y_5 - y_4)
    if error == 0:
        s = 2.0
    else:
        s = 0.84 * (tol / error) ** 0.25
    
    h_new = h * max(0.1, min(4.0, s))
    
    if error <= tol:
        return y_5, t + h, h_new
    else:
        return y, t, h_new

def newton_raphson(
    f: Callable[[np.ndarray], np.ndarray], 
    x0: np.ndarray, 
    jac: Callable[[np.ndarray], np.ndarray] = None, 
    tol: float = 1e-6, 
    max_iter: int = 100
) -> np.ndarray:
    x = np.array(x0, dtype=float)
    for _ in range(max_iter):
        fx = f(x)
        if np.linalg.norm(fx) < tol:
            return x
            
        if jac is None:
            n = len(x)
            J = np.zeros((n, n))
            eps = 1e-8
            for i in range(n):
                x_eps = x.copy()
                x_eps[i] += eps
                J[:, i] = (f(x_eps) - fx) / eps
        else:
            J = jac(x)
            
        try:
            dx = np.linalg.solve(J, -fx)
        except np.linalg.LinAlgError:
            dx = -fx / (np.diag(J) + 1e-6)
            
        x += dx
    return x
