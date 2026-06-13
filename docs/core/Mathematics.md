# SADS — Mathematics Foundation

**Document ID:** SADS-MTH-001
**Revision:** 1.0

---

## 1. Scope

This document catalogs the mathematical foundations used throughout the SADS engineering engines. All equations, solver methods, and numerical techniques are referenced here.

---

## 2. Orbital Mechanics

### 2.1 Kepler's Third Law

The orbital period of a body on a closed orbit around a central mass:

$$T = 2\pi \sqrt{\frac{a^3}{\mu}}$$

where:
- `a` = semi-major axis [m]
- `μ = GM` = standard gravitational parameter [m³/s²]
- For Earth: `μ_E = 3.986004418 × 10¹⁴ m³/s²`

### 2.2 Vis-Viva Equation

The speed of a body at any point in its orbit:

$$v = \sqrt{\mu \left( \frac{2}{r} - \frac{1}{a} \right)}$$

### 2.3 Orbit Equation (Conic Section)

$$r = \frac{a(1-e^2)}{1 + e \cos \nu}$$

where:
- `r` = radius from central body [m]
- `e` = eccentricity [-]
- `ν` = true anomaly [rad]

### 2.4 Classical Orbital Elements

Six elements fully describe an unperturbed orbit:
1. Semi-major axis `a` [m]
2. Eccentricity `e` [-]
3. Inclination `i` [rad]
4. Right Ascension of Ascending Node `Ω` [rad]
5. Argument of periapsis `ω` [rad]
6. True anomaly `ν` [rad]

### 2.5 J2 Perturbation (RAAN drift)

$$\dot{\Omega} = -\frac{3}{2} n J_2 \left(\frac{R_E}{a}\right)^2 \frac{\cos i}{(1-e^2)^2}$$

with `J_2 = 1.08263 × 10⁻³` for Earth.

### 2.6 Hohmann Transfer

Two-impulse transfer between coplanar circular orbits:

$$\Delta v_1 = \sqrt{\frac{\mu}{r_1}} \left( \sqrt{\frac{2 r_2}{r_1 + r_2}} - 1 \right)$$

$$\Delta v_2 = \sqrt{\frac{\mu}{r_2}} \left( 1 - \sqrt{\frac{2 r_1}{r_1 + r_2}} \right)$$

Transfer time:

$$\Delta t = \pi \sqrt{\frac{(r_1 + r_2)^3}{8\mu}}$$

### 2.7 Lambert's Problem

Find the transfer orbit connecting two position vectors in a given time:

$$ \Delta \nu = f(\mathbf{r}_1, \mathbf{r}_2, \Delta t) $$

Solved via universal-variable formulation (Bate-Mueller-White) or Gooding's algorithm.

### 2.8 Patched Conics

For interplanetary missions, the trajectory is approximated as a sequence of two-body problems separated by spheres of influence.

### 2.9 N-Body Dynamics

For high-fidelity propagation:

$$\ddot{\mathbf{r}}_i = -\sum_{j \neq i} \frac{G m_j (\mathbf{r}_i - \mathbf{r}_j)}{|\mathbf{r}_i - \mathbf{r}_j|^3}$$

Integrated with RK4 or RK45 (Dormand-Prince).

---

## 3. Control Theory

### 3.1 Rigid-Body Dynamics (Euler's Equations)

$$I_1 \dot{\omega}_1 - (I_2 - I_3)\omega_2 \omega_3 = \tau_1$$
$$I_2 \dot{\omega}_2 - (I_3 - I_1)\omega_3 \omega_1 = \tau_2$$
$$I_3 \dot{\omega}_3 - (I_1 - I_2)\omega_1 \omega_2 = \tau_3$$

### 3.2 PID Control

$$u(t) = K_p e(t) + K_i \int e(\tau) d\tau + K_d \frac{de}{dt}$$

Tuning: Ziegler-Nichols, Tyreus-Luyben, or LQR-based.

### 3.3 Linear Quadratic Regulator (LQR)

Minimize:

$$J = \int_0^\infty \left( \mathbf{x}^T Q \mathbf{x} + \mathbf{u}^T R \mathbf{u} \right) dt$$

Subject to: $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$

Solution: $\mathbf{u} = -K\mathbf{x}$ where $K$ solves the algebraic Riccati equation.

### 3.4 Kalman Filter

Prediction:

$$\hat{\mathbf{x}}_{k|k-1} = F_k \hat{\mathbf{x}}_{k-1|k-1} + B_k \mathbf{u}_k$$
$$P_{k|k-1} = F_k P_{k-1|k-1} F_k^T + Q_k$$

Update:

$$K_k = P_{k|k-1} H_k^T (H_k P_{k|k-1} H_k^T + R_k)^{-1}$$
$$\hat{\mathbf{x}}_{k|k} = \hat{\mathbf{x}}_{k|k-1} + K_k (\mathbf{z}_k - H_k \hat{\mathbf{x}}_{k|k-1})$$

### 3.5 Model Predictive Control (MPC)

Solve at each time step:

$$\min_{\mathbf{u}} \sum_{k=0}^{N-1} \ell(\mathbf{x}_k, \mathbf{u}_k) + V_f(\mathbf{x}_N)$$

subject to dynamics and constraints, apply first control, repeat (receding horizon).

---

## 4. Thermal Physics

### 4.1 Stefan-Boltzmann Law

$$Q = \varepsilon \sigma A T^4$$

where:
- `ε` = emissivity [-]
- `σ = 5.670374419 × 10⁻⁸ W/m²/K⁴`
- `A` = area [m²]
- `T` = absolute temperature [K]

### 4.2 Fourier Heat Conduction

$$Q = -k A \frac{dT}{dx}$$

For a slab: $Q = \frac{kA \Delta T}{L}$

### 4.3 Convective Heat Transfer

$$Q = h A (T_s - T_\infty)$$

where `h` = convective heat transfer coefficient [W/m²/K].

### 4.4 Thermal Equilibrium

At steady state: $Q_{in} = Q_{out}$

For a node with radiation only:

$$\alpha S A_\odot + Q_{internal} = \varepsilon \sigma A_{rad} T^4$$

---

## 5. Electromagnetics & Communications

### 5.1 Free-Space Path Loss

$$L_{fs} = \left(\frac{4\pi d}{\lambda}\right)^2$$

In decibels:

$$L_{fs,dB} = 20 \log_{10}\left(\frac{4\pi d}{\lambda}\right)$$

### 5.2 Antenna Gain (Parabolic)

$$G = \eta \left(\frac{\pi D}{\lambda}\right)^2$$

$$G_{dBi} = 10 \log_{10} G$$

### 5.3 Half-Power Beamwidth

$$\theta_{3dB} \approx 70 \frac{\lambda}{D}$$

### 5.4 Link Budget Equation

$$\frac{C}{N_0} = \text{EIRP} + \frac{G_R}{T_s} - L_{fs} - L_{atm} - k$$

In dB:

$$[C/N_0] = [\text{EIRP}] + [G_R/T_s] - [L_{fs}] - [L_{atm}] - [k_{dB}]$$

### 5.5 Shannon Capacity

$$C = B \log_2 \left(1 + \frac{S}{N}\right)$$

Required energy per bit:

$$\frac{E_b}{N_0} = \frac{C/N_0}{R_b}$$

### 5.6 BER for BPSK

$$P_b = Q\left(\sqrt{\frac{2 E_b}{N_0}}\right) = \frac{1}{2} \text{erfc}\left(\sqrt{\frac{E_b}{N_0}}\right)$$

---

## 6. Propulsion

### 6.1 Tsiolkovsky Rocket Equation

$$\Delta v = I_{sp} g_0 \ln \frac{m_0}{m_f}$$

Solving for propellant:

$$m_p = m_0 \left(1 - e^{-\Delta v / (I_{sp} g_0)}\right)$$

### 6.2 Mass Fraction

$$\zeta = \frac{m_p}{m_0} = 1 - e^{-\Delta v / (I_{sp} g_0)}$$

### 6.3 Thrust and Mass Flow

$$F = \dot{m} v_e = \dot{m} I_{sp} g_0$$

### 6.4 Electric Propulsion Power Throttling

$$P_{in} = \frac{F \cdot I_{sp} \cdot g_0}{2 \eta_{thrust}}$$

where `η_thrust` = thrust efficiency (typically 0.4–0.7 for Hall thrusters).

---

## 7. Numerical Methods

### 7.1 Runge-Kutta 4 (RK4)

For $\dot{y} = f(t, y)$:

```
k1 = f(t, y)
k2 = f(t + h/2, y + h*k1/2)
k3 = f(t + h/2, y + h*k2/2)
k4 = f(t + h, y + h*k3)
y_{n+1} = y_n + (h/6)(k1 + 2k2 + 2k3 + k4)
```

### 7.2 Runge-Kutta 45 (Dormand-Prince)

Adaptive step size, 5th-order accurate with 6th-order error estimate. Used by `scipy.integrate.solve_ivp`.

### 7.3 Finite Difference

Approximates derivatives:

$$f'(x) \approx \frac{f(x+h) - f(x-h)}{2h} \quad \text{(central)}$$

For thermal: discretize $\nabla^2 T$ on a mesh.

### 7.4 Finite Element (FEM)

Weak form: find $u$ such that

$$\int_\Omega \nabla u \cdot \nabla v \, d\Omega = \int_\Omega f v \, d\Omega \quad \forall v$$

Discretized on a mesh, solved as a linear system.

### 7.5 Monte Carlo

Statistical estimation:

$$\hat{I} = \frac{1}{N} \sum_{i=1}^N g(X_i)$$

### 7.6 Newton's Method

For $f(x) = 0$:

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

Used for thermal equilibrium, Kepler equation.

### 7.7 Kepler Equation Solver

$$M = E - e \sin E$$

Solved iteratively (Newton):

$$E_{n+1} = E_n - \frac{E_n - e \sin E_n - M}{1 - e \cos E_n}$$

---

## 8. Linear Algebra

### 8.1 Rotation Matrices

3-1-2 (yaw-pitch-roll) Euler sequence:

$$R = R_z(\psi) R_y(\theta) R_x(\phi)$$

Quaternions preferred for numerical stability:

$$\mathbf{q} = [q_w, q_x, q_y, q_z], \quad |\mathbf{q}| = 1$$

### 8.2 Inertia Tensor

$$I_{xx} = \sum_i m_i (y_i^2 + z_i^2) - M(\bar{y}^2 + \bar{z}^2)$$

---

## 9. Statistics & Uncertainty

### 9.1 Propagation of Uncertainty

For $y = f(x_1, \ldots, x_n)$:

$$\sigma_y^2 = \sum_i \left(\frac{\partial f}{\partial x_i}\right)^2 \sigma_{x_i}^2 + 2 \sum_{i<j} \frac{\partial f}{\partial x_i} \frac{\partial f}{\partial x_j} \text{cov}(x_i, x_j)$$

### 9.2 Sobol Sensitivity Indices

First-order:
$$S_i = \frac{V[E[Y|X_i]]}{V[Y]}$$

### 9.3 Reliability Metrics

For exponential distribution (constant hazard):

$$R(t) = e^{-\lambda t}, \quad \text{MTBF} = \frac{1}{\lambda}$$
