# SADS — Mathematical Algorithms Cookbook

**Document ID:** SADS-MTH-ALG-001  
**Revision:** 1.0  
**Classification:** Engineering Reference — Implementation Recipes  

---

## 1. Kepler Equation Solver

Solves the transcendental Kepler equation $M = E - e \sin E$ for the eccentric anomaly $E$ given the mean anomaly $M$ and eccentricity $e$.

### 1.1 Mathematical Formulation
We define the function:

$$f(E) = E - e \sin E - M = 0$$

Newton-Raphson update rule:

$$E_{k+1} = E_k - \frac{f(E_k)}{f'(E_k)} = E_k - \frac{E_k - e \sin E_k - M}{1 - e \cos E_k}$$

### 1.2 Python Implementation Recipe
```python
import numpy as np

def solve_kepler(M: float, e: float, tol: float = 1e-12, max_iter: int = 100) -> float:
    """
    Solves Kepler's equation for eccentric anomaly E.
    M: Mean anomaly in radians.
    e: Eccentricity (0 <= e < 1).
    """
    # Mikkola's or simple high-quality initial guess
    E = M + 0.85 * e * np.sign(np.sin(M))
    
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        df = 1.0 - e * np.cos(E)
        
        dE = f / df
        E -= dE
        
        if abs(dE) < tol:
            return E
            
    raise RuntimeError("Kepler solver failed to converge.")
```

---

## 2. Nodal Thermal Solver (Newton-Raphson System)

Solves the steady-state multi-node thermal equilibrium equations where radiation terms introduce fourth-power non-linearities.

### 2.1 Mathematical Formulation
For $N$ coupled nodes, the residual equation for node $i$ is:

$$F_i(\mathbf{T}) = Q_{\text{in}, i} + \sum_{j} K_{ij}(T_j - T_i) + \sum_{j} R_{ij}\sigma(T_j^4 - T_i^4) - \epsilon_i \sigma A_i T_i^4 = 0$$

The elements of the Jacobian matrix $J$ are:

$$J_{ii} = \frac{\partial F_i}{\partial T_i} = -\sum_{j} K_{ij} - 4 T_i^3 \sigma \left( \epsilon_i A_i + \sum_{j} R_{ij} \right)$$

$$J_{ij} = \frac{\partial F_i}{\partial T_j} = K_{ij} + 4 T_j^3 \sigma R_{ij} \quad (i \neq j)$$

### 2.2 Python Implementation Recipe
```python
def solve_nodal_thermal(q_in: np.ndarray, K: np.ndarray, R: np.ndarray, 
                        eps: np.ndarray, area: np.ndarray, 
                        T_init: np.ndarray, tol: float = 1e-6, max_iter: int = 50) -> np.ndarray:
    """
    Solves steady-state thermal nodal temperatures.
    K: Conductive coupling matrix (N x N).
    R: Radiative View-factor matrix (N x N).
    """
    SIGMA = 5.670374419e-8
    T = np.copy(T_init)
    N = len(T)
    
    for _ in range(max_iter):
        # Calculate residuals F(T)
        F = np.zeros(N)
        J = np.zeros((N, N))
        
        for i in range(N):
            cond_sum = sum(K[i, j] * (T[j] - T[i]) for j in range(N))
            rad_sum = sum(R[i, j] * SIGMA * (T[j]**4 - T[i]**4) for j in range(N))
            emit = eps[i] * SIGMA * area[i] * T[i]**4
            
            F[i] = q_in[i] + cond_sum + rad_sum - emit
            
            # Setup Jacobian row
            for j in range(N):
                if i == j:
                    J[i, i] = -sum(K[i, k] for k in range(N)) - 4 * T[i]**3 * SIGMA * (eps[i] * area[i] + sum(R[i, k] for k in range(N)))
                else:
                    J[i, j] = K[i, j] + 4 * T[j]**3 * SIGMA * R[i, j]
                    
        # Newton update
        try:
            dT = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            # Fallback to pseudo-inverse if singular
            dT = np.linalg.pinv(J) @ -F
            
        T += dT
        T = np.clip(T, 50.0, 450.0) # Physical clamping bounds
        
        if np.linalg.norm(dT) < tol:
            return T
            
    return T
```

---

## 3. Communications Link Budget Analyzer

Calculates free-space loss and received carrier-to-noise ratio ($C/N_0$) at ground stations.

### 3.1 Python Implementation Recipe
```python
def analyze_link_budget(f_hz: float, tx_power_w: float, d_km: float, 
                        g_tx_dbi: float, g_rx_dbi: float, 
                        t_sys_k: float = 290.0) -> dict:
    """
    Computes Friis path loss and Eb/N0 margins.
    """
    C = 299792458.0
    K_B = 1.380649e-23
    K_DB = 10 * np.log10(K_B)
    
    lam = C / f_hz
    d_m = d_km * 1000.0
    
    # Path loss
    fspl_db = 20 * np.log10(4 * np.pi * d_m / lam)
    
    # Received C/N0
    eirp_dbw = 10 * np.log10(tx_power_w) + g_tx_dbi
    cn_ratio_db = eirp_dbw + g_rx_dbi - fspl_db - (10 * np.log10(t_sys_k) + K_DB)
    
    return {
        "wavelength_m": lam,
        "path_loss_db": fspl_db,
        "eirp_dbw": eirp_dbw,
        "cn_db": cn_ratio_db,
        "link_closed": cn_ratio_db >= 10.0
    }
```

---

## 4. Orbit Propagator with J2 Perturbation (Numerical)

Propagates the spacecraft state vector $\mathbf{x} = [\mathbf{r}, \mathbf{v}]$ in LEO with Earth oblate perturbations.

### 4.1 Python Implementation Recipe
```python
def j2_derivative(t: float, y: np.ndarray, mu: float = 3.986004418e14, 
                  R_E: float = 6378137.0, J2: float = 1.08263e-3) -> np.ndarray:
    """
    y = [rx, ry, rz, vx, vy, vz]
    Returns dy/dt = [vx, vy, vz, ax, ay, az]
    """
    r_vec = y[0:3]
    v_vec = y[3:6]
    r = np.linalg.norm(r_vec)
    
    # Two-body acceleration
    a_2body = -mu * r_vec / r**3
    
    # J2 perturbations
    z = r_vec[2]
    factor = 1.5 * J2 * mu * R_E**2 / r**5
    
    a_j2 = np.zeros(3)
    a_j2[0] = factor * (r_vec[0] * (5.0 * z**2 / r**2 - 1.0))
    a_j2[1] = factor * (r_vec[1] * (5.0 * z**2 / r**2 - 1.0))
    a_j2[2] = factor * (r_vec[2] * (5.0 * z**2 / r**2 - 3.0))
    
    dy = np.zeros(6)
    dy[0:3] = v_vec
    dy[3:6] = a_2body + a_j2
    return dy
```
