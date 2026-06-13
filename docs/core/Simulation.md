# SADS — Simulation Engine Specifications

**Document ID:** SADS-SIM-001
**Revision:** 1.0

---

## 1. Introduction

The SADS Simulation Engine is a multi-disciplinary simulation environment designed to execute coupled orbital, thermal, electrical power, and communication link analyses. It translates visual system diagrams into systems of differential-algebraic equations (DAEs) and solves them over orbital timelines.

---

## 2. Solver Architecture

The simulation service coordinates individual subsystem solvers. Data flows between subsystems at each time step using an event-driven execution framework:

```
                  ┌──────────────────────┐
                  │    Orbit Propagator  │
                  └──────────┬───────────┘
                             │ Altitude, Sun Vector, Earth Vector
                             ▼
                  ┌──────────────────────┐
                  │    Thermal Solver    │ ◄── Dissipation Heat
                  └──────────┬───────────┘
                             │ Node Temperatures
                             ▼
                  ┌──────────────────────┐
                  │    EPS Solar/Power   │ ◄── Solar Cell Temp Corrected
                  └──────────┬───────────┘
                             │ Battery Voltage, Power Margins
                             ▼
                  ┌──────────────────────┐
                  │     Link Budget      │
                  └──────────────────────┘
```

---

## 3. Propagation & Numerical Solvers

SADS uses both low-latency analytical solvers for rapid workspace iterations and high-fidelity numerical solvers for timeline studies.

### 3.1 Time-Step Methods
* **Fixed Time-Step Integrators:** Standard Runge-Kutta 4th-order (RK4) solvers run at fixed intervals (typically $10\text{ s}$ to $60\text{ s}$) to balance execution speed and integration error.
* **Adaptive Time-Step Integrators:** Dormand-Prince (RK45) methods are applied for highly eccentric orbits and precise thrust maneuver calculations where local truncation errors must be bound:
  $$\text{LTE} = |y_{5th} - y_{4th}| \le \text{Tol}_{abs} + \text{Tol}_{rel} |y|$$

### 3.2 Orbit Propagation
Orbits are propagated in the Earth-Centered Inertial (ECI) frame:

$$\ddot{\mathbf{r}} = -\frac{\mu_E}{r^3} \mathbf{r} + \mathbf{a}_{per}$$

Perturbations include:
* **Earth Oblateness ($J_2$):**
  $$\mathbf{a}_{J2} = -\frac{3 J_2 \mu_E R_E^2}{2 r^5} \left[ \left(1 - \frac{5z^2}{r^2}\right) \mathbf{r} + 2z \hat{\mathbf{z}} \right]$$
* **Atmospheric Drag:** Applied below $800\text{ km}$ using Harris-Priester or exponential density models:
  $$\mathbf{a}_{drag} = -\frac{1}{2} \rho \frac{C_D A_{drag}}{m} v_{rel} \mathbf{v}_{rel}$$

---

## 4. Subsystem Solver Iteration Loops

### 4.1 EPS Solar Generation & Charger Loop
Solar panel efficiency varies inversely with cell temperature. At each step, SADS corrects power outputs:

$$P_{actual} = P_{nominal} \cdot \left[1 - \gamma_{temp} (T_{cell} - T_{ref})\right]$$

where:
- $\gamma_{temp}$ = temperature coefficient of GaAs/Si cells (typically 0.08%/K to 0.23%/K)
- $T_{ref}$ = reference temperature ($25^\circ\text{C}$).

### 4.2 Nodal Thermal Solver (Newton-Raphson)
The thermal state of the spacecraft is modeled as a lumped parameter network of $N$ thermal masses (nodes). For node $i$:

$$m_i C_i \frac{dT_i}{dt} = Q_{in, i} - \sum_{j} K_{ij} (T_i - T_j) - \sum_{j} R_{ij} \sigma (T_i^4 - T_j^4) - \epsilon_i \sigma A_i T_i^4$$

where:
- $m_i C_i$ = thermal capacity of node $i$ [J/K]
- $K_{ij}$ = conductive heat transfer coefficient between $i$ and $j$
- $R_{ij}$ = radiative view-factor exchange coefficient between $i$ and $j$.

For steady-state thermal profiles ($\frac{dT_i}{dt} = 0$), SADS solves the resulting system of non-linear algebraic equations using the Newton-Raphson method. The Jacobian matrix $J$ contains elements:

$$J_{ik} = \frac{\partial f_i}{\partial T_k}$$

$$T^{(n+1)} = T^{(n)} - J^{-1} F(T^{(n)})$$

This solver converges in 4 to 8 iterations for standard satellite layouts.
