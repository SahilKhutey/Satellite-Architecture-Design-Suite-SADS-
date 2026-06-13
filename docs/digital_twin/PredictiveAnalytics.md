# SADS Digital Twin Reference — Predictive Analytics

**Document ID:** SADS-TWN-ANA-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

SADS analyzes telemetry trends to predict potential satellite failures (e.g. battery degradation, thermal spikes, propellant depletion).

---

## 2. Predictive Models
* **Battery Degradation**: Extrapolates capacity fading based on depth-of-discharge (DoD) counts.
* **Thermal Out-of-Bounds**: Warns when simulated seasonal thermal changes will push node temperatures past qualification limits.
