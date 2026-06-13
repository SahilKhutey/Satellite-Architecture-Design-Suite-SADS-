# SADS Simulation Reference — Design Optimization

**Document ID:** SADS-SIM-OPT-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

SADS includes gradient-based and heuristic optimization loops (e.g. active area sizing, structural mass minimization).

---

## 2. Algorithms

The optimization agent leverages the following methodologies:
* **EPS Sizing**: Solves for minimum solar array area and battery Wh capacity to maintain a 20% power margin:
  $$\min (A_{\text{panel}} \cdot \text{Cost}_{\text{panel}} + C_{\text{battery}} \cdot \text{Cost}_{\text{battery}})$$
  Subject to:
  $$\text{DoD} \le 0.50$$
  $$\text{Margin}_{\text{power}} \ge 0.20$$
