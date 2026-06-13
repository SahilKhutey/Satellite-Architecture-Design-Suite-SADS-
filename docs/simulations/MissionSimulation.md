# Mission Simulation Orchestration Reference

## 1. Timeline Integration
The SADS simulation manager schedules phase transitions and updates concurrent subsystems:
- **Orbit Phase:** Steps orbital positions and updates sun visibility vectors.
- **Power Phase:** Executes array generation and computes battery level status.
- **Thermal Phase:** Computes radiation and heating node states.
- **ADCS & Comm Phase:** Evaluates pointing offsets and transmission packet margins.

## 2. Event-Driven Logic
Simulation triggers include:
- `ECLIPSE_ENTRY`: Disables solar panels, switches thermal load to minimums.
- `MANEUVER_START`: Enables propulsion burns, consumes fuel, imposes ADCS torque commands.
