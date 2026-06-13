# SADS Subsystem Reference — Orbit Engine

**Document ID:** SADS-SUB-ORB-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

The Orbit Subsystem provides trajectory propagation, orbital mechanics solvers, perturbation modeling (J2 gravity coefficient, atmospheric drag, solar radiation pressure), and delta-V maneuver budget planning.

---

## 2. Mathematical and Physics Models

### 2.1 Keplerian Propagation
Resolves motion under two-body gravitation:
$$\ddot{\vec{r}} = -\frac{\mu}{r^3}\vec{r}$$
Where $\mu = 3.986004418 \times 10^{14} \text{ m}^3/\text{s}^2$ for Earth.

### 2.2 Kepler's Equation
Solves mean anomaly $M$ to eccentric anomaly $E$:
$$M = E - e\sin E$$
Solved numerically via Newton-Raphson iteration.

### 2.3 Hohmann Orbit Transfer
Determines velocity changes for co-planar circular transfers:
$$\Delta V_1 = \sqrt{\frac{\mu}{r_1}} \left( \sqrt{\frac{2r_2}{r_1 + r_2}} - 1 \right)$$
$$\Delta V_2 = \sqrt{\frac{\mu}{r_2}} \left( 1 - \sqrt{\frac{2r_1}{r_1 + r_2}} \right)$$

---

## 3. Configuration and API Interfaces

The orbit engine can be configured using circular altitude and orbit parameters:
- `altitude_km`: Subsatellite altitude in kilometers.
- `orbital_period_s()`: Returns the calculated orbital period in seconds.
