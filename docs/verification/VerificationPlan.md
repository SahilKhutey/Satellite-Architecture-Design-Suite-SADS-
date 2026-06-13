# Verification Plan

## 1. Scope
Ensures SADS simulation engines calculate values matching exact physics formulations.

## 2. Test Suites
- **Unit Verification:** Validates individual modules (e.g. orbit periods, antenna gains, solar efficiency).
- **Integration Verification:** Verifies API payload models and pipeline data flow.
- **Subsystem Verification:** Validates coupled EPS and thermal runs.

## 3. Threshold Limits
- Orbit period must match analytical calculation within $0.01\%$.
- Link budget must match standard radar range calculations within $0.05\text{ dB}$.
- Radiative balance solver must reach convergence tolerances within $10^{-6}\text{ K}$.
