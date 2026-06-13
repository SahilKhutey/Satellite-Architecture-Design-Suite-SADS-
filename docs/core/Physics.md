# Satellite Architecture Design Suite (SADS) — Physics Principles & Engineering Foundations

**Document ID:** SADS-PHY-PRIN-001  
**Revision:** 1.0  
**Classification:** Engineering Reference — Foundational  
**Status:** Approved  

---

## 0. Document Purpose

This document is the **scientific and engineering backbone** of the Satellite Architecture Design Suite. It defines the physical laws, engineering principles, mathematical foundations, and numerical models used by every subsystem engine in the platform.

The objective is to ensure that **all subsystem simulations are based on physically accurate, dimensionally consistent, and verifiable models** — and that every result produced by SADS is traceable to a first-principles derivation.

### 0.1 Scope
This document covers:
- The 12 physics domains underlying SADS
- Governing equations and assumptions
- Validity ranges and engineering tolerances
- Verification criteria for each engine
- Fidelity levels and their appropriate use

### 0.2 Document Hierarchy
```
SADS-DOC-PYRAMID
    ├── Mathematics.md       ← formulas, solvers
    ├── Physics.md           ← (this file) physical laws & principles
    ├── Physics_Reference.md  ← deep reference (constants, materials data)
    ├── Simulation.md        ← engine orchestration
    └── Verification.md      ← V&V of physics implementation
```

---

## 1. Physics Domains

The SADS platform is built upon twelve primary physics domains. Each domain maps to one or more engine modules.

| # | Domain | SADS Engine | Typical Use |
|---|--------|-------------|-------------|
| 1 | Classical Mechanics | All engines (foundational) | Motion, force, momentum |
| 2 | Orbital Mechanics | `orbit_engine.py` | Trajectory, propagation |
| 3 | Thermodynamics | `thermal_engine.py` | Energy balance, heat |
| 4 | Heat Transfer | `thermal_engine.py` | Conduction, radiation |
| 5 | Electromagnetics | `comm_engine.py` | Antennas, propagation |
| 6 | Plasma Physics | `propulsion_engine.py` | Electric propulsion |
| 7 | Rocket Propulsion | `propulsion_engine.py` | ΔV, mass budgets |
| 8 | Rigid Body Dynamics | `adcs_engine.py` | Attitude, pointing |
| 9 | Control Systems | `adcs_engine.py` | PID, LQR, Kalman |
| 10 | Radiation Physics | `power_engine.py` | Solar, particle, dose |
| 11 | Space Environment | `orbit_engine.py`, thermal | Drag, SRP, debris |
| 12 | Materials Physics | All engines | Density, conductivity, yield |

---

## 2. Classical Mechanics

The foundation of all spacecraft motion.

### 2.1 Newton's First Law (Inertia)
If the net force $\sum \mathbf{F} = 0$, then linear momentum is constant:
$$\dot{\mathbf{p}} = 0$$

* **SADS Applications:** Spacecraft coast phases and momentum conservation checks.

### 2.2 Newton's Second Law
$$\mathbf{F} = m \mathbf{a} = m \frac{d^2 \mathbf{r}}{dt^2}$$

For variable mass systems (rocket thrust):
$$\mathbf{F}_{ext} = m \frac{d\mathbf{v}}{dt} - \dot{m} \mathbf{v}_{rel}$$
where $\mathbf{v}_{rel}$ is the velocity of ejected mass relative to the vehicle.

### 2.3 Newton's Third Law
$$\mathbf{F}_{AB} = -\mathbf{F}_{BA}$$

* **SADS Applications:** Propulsion thrust generation and reaction wheel torque feedback.

---

## 3. Orbital Mechanics

### 3.1 Universal Gravitation
$$\mathbf{F} = -G \frac{m_1 m_2}{r^3} \mathbf{r}$$

### 3.2 Kepler's Laws
1. **First Law (Ellipses):** Orbits are conic sections.
   $$r = \frac{a(1 - e^2)}{1 + e \cos \nu}$$
2. **Second Law (Equal Areas):** Angular momentum conservation:
   $$\frac{dA}{dt} = \frac{1}{2} r^2 \dot{\nu} = \text{const}$$
3. **Third Law (Harmonic):** Period and semi-major axis relation:
   $$T = 2\pi\sqrt{\frac{a^3}{\mu}}$$

---

## 4. Thermodynamics & Heat Transfer

### 4.1 Laws of Thermodynamics
* **First Law (Energy Conservation):**
  $$Q_{in} - Q_{out} = m c_p \frac{dT}{dt}$$
* **Second Law:** Heat naturally flows from hot to cold regions, increasing entropy.

### 4.2 Nodal Thermal Model
For a spacecraft node in thermal equilibrium:

$$\alpha S A_\odot F_{sun} + q_{albedo} + q_{IR} + Q_{internal} = \varepsilon \sigma A_{rad} T^4$$

---

## 5. Electromagnetics & Communications

### 5.1 Friis Transmission Equation
The received power at distance $d$ is:
$$P_r = P_t G_t G_r \left(\frac{\lambda}{4\pi d}\right)^2$$

### 5.2 Antenna Gain (Parabolic reflector)
$$G = \eta \left(\frac{\pi D}{\lambda}\right)^2$$

---

## 6. Plasma Physics & Electric Propulsion

### 6.1 Charged Particle Motion (Lorentz Force)
$$\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})$$

### 6.2 Specific Impulse (Electric)
$$I_{sp} = \frac{1}{g_0}\sqrt{\frac{2 e V_{\text{beam}}}{m_{ion}}}$$

---

## 7. Rocket Propulsion Physics

### 7.1 Rocket Equation (Tsiolkovsky)
$$\Delta v = I_{sp} g_0 \ln\left(\frac{m_0}{m_f}\right)$$

---

## 8. Rigid Body Dynamics & Control

### 8.1 Attitude Dynamics (Euler's Equations)
$$\boldsymbol{\tau} = I \boldsymbol{\alpha} + \boldsymbol{\omega} \times (I \boldsymbol{\omega})$$

### 8.2 Kalman State Estimation
Prediction and update updates of spacecraft state vector $\hat{\mathbf{x}}$ and covariance matrix $P$.

---

## 9. Space Environment Physics

* **Atmospheric Drag:** Applied below $800\text{ km}$ altitude:
  $$F_d = \frac{1}{2} \rho v^2 C_d A$$
* **Solar Radiation Pressure (SRP):**
  $$F_{SRP} = \frac{S}{c} A (1 + \rho_s) \cos\theta$$

---

## 10. References
- Vallado, D. A., *Fundamentals of Astrodynamics and Applications*.
- Fortescue, P., Swinerd, G., Stark, J., *Spacecraft Systems Engineering*.
