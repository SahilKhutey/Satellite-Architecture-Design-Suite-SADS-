# SADS Scientific - Optimization Solvers
import numpy as np
from typing import Callable

def gradient_descent(
    f: Callable[[np.ndarray], float], 
    x0: np.ndarray, 
    grad: Callable[[np.ndarray], np.ndarray] = None, 
    lr: float = 0.01, 
    tol: float = 1e-6, 
    max_iter: int = 1000
) -> np.ndarray:
    x = np.array(x0, dtype=float)
    for _ in range(max_iter):
        if grad is None:
            n = len(x)
            g = np.zeros(n)
            eps = 1e-8
            fx = f(x)
            for i in range(n):
                x_eps = x.copy()
                x_eps[i] += eps
                g[i] = (f(x_eps) - fx) / eps
        else:
            g = grad(x)
            
        if np.linalg.norm(g) < tol:
            return x
            
        x -= lr * g
    return x

def nelder_mead(
    f: Callable[[np.ndarray], float], 
    x0: np.ndarray, 
    step: float = 0.1, 
    no_improve_thr: float = 1e-6, 
    no_improv_break: int = 10, 
    max_iter: int = 1000
) -> np.ndarray:
    dim = len(x0)
    prev_best = f(x0)
    no_improv = 0
    
    res = [[x0, prev_best]]
    for i in range(dim):
        x = x0.copy()
        x[i] += step
        score = f(x)
        res.append([x, score])
        
    for _ in range(max_iter):
        res.sort(key=lambda x: x[1])
        best = res[0][1]
        
        if best < prev_best - no_improve_thr:
            no_improv = 0
            prev_best = best
        else:
            no_improv += 1
            if no_improv >= no_improv_break:
                return res[0][0]
                
        centroid = np.mean([x[0] for x in res[:-1]], axis=0)
        
        xr = centroid + (centroid - res[-1][0])
        rscore = f(xr)
        if res[0][1] <= rscore < res[-2][1]:
            del res[-1]
            res.append([xr, rscore])
            continue
            
        if rscore < res[0][1]:
            xe = centroid + 2.0 * (xr - centroid)
            escore = f(xe)
            if escore < rscore:
                del res[-1]
                res.append([xe, escore])
            else:
                del res[-1]
                res.append([xr, rscore])
            continue
            
        xc = centroid + 0.5 * (res[-1][0] - centroid)
        cscore = f(xc)
        if cscore < res[-1][1]:
            del res[-1]
            res.append([xc, cscore])
            continue
            
        x1 = res[0][0]
        nres = [[x1, res[0][1]]]
        for x, _ in res[1:]:
            xn = x1 + 0.5 * (x - x1)
            nres.append([xn, f(xn)])
        res = nres
        
    return res[0][0]
