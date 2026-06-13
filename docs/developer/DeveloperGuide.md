# SADS Developer Guide

## 1. Onboarding and Workspace Setup

Ensure Python 3.11+ is installed.
1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

## 2. Package Architecture
* `engines/`: Core physics engines (Power, Thermal, ADCS, Comm, Orbit).
* `mbse/`: Systems engineering models.
* `ai/`: Optimization and advisor agents.
* `digital_twin/`: Kalman filter state synchronizers and telemetry streams.
* `tests/`: Extensive V&V verification suites.
