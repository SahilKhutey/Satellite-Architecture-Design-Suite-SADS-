# SADS Digital Twin Reference — State Estimation

**Document ID:** SADS-TWN-EST-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

To synchronize digital twins with physical satellites, SADS applies a steady-state Kalman-style filter gain update step.

---

## 2. Estimation Model

Given a prediction value $x_{k|k-1}$ and a measured sensor reading $z_k$, SADS applies a filter correction:
$$x_{k|k} = x_{k|k-1} + K (z_k - x_{k|k-1})$$
Where $K$ represents the configured filter gain. This provides robust estimation for thermal temperatures, power levels, and ADCS attitude drift tracking.
