# SADS Simulation Reference — Numerical Methods

**Document ID:** SADS-SIM-NUM-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Mathematical Integrators

SADS provides two primary numeric integrators for orbital and thermal equations:

### 1.1 Runge-Kutta 4th Order (RK4)
Used for fast orbital propagation:
$$k_1 = f(t_n, y_n)$$
$$k_2 = f\left(t_n + \frac{h}{2}, y_n + h\frac{k_1}{2}\right)$$
$$k_3 = f\left(t_n + \frac{h}{2}, y_n + h\frac{k_2}{2}\right)$$
$$k_4 = f(t_n + h, y_n + h k_3)$$
$$y_{n+1} = y_n + \frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

### 1.2 Newton-Raphson Solver
Used for thermal equilibrium equations:
$$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}$$
Ensures that radiative and conductive heat exchanges balance.
