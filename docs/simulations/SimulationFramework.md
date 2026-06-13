# SADS Simulation Reference — Simulation Framework

**Document ID:** SADS-SIM-FWK-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

SADS employs a modular, time-stepped simulation architecture. Each subsystem engine registers with the main event loop, reading input states and propagating states dynamically.

---

## 2. Integration Architecture

The main simulation engine manages coordination:
1. **Clock Generator**: Generates discrete time steps $\Delta t$.
2. **State Register**: Main telemetry cache storing the states of all subsystems.
3. **Execution Steps**:
   - Update orbit propagation
   - Calculate solar panel illumination state (eclipse/sunlit)
   - Evaluate battery charging/discharging rates
   - Compute nodal thermal heat exchanges
   - Audit ADCS feedback controls
