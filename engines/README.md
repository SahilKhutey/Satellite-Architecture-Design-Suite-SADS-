# SADS Subsystem Engineering Engines

This directory contains the core physical and mathematical engines used by the Satellite Architecture Design Suite (SADS) for spacecraft simulations.

## Package Architecture

```
engines/
├── orbit-engine/             # Trajectory & orbital propagation
├── power-engine/             # Solar & battery charging model
├── thermal-engine/           # Radiative temperature nodal solver
├── communications-engine/    # Link budget computations
├── propulsion-engine/        # Rocket mass fraction calculations
├── adcs-engine/              # Slew rate & pointing budget checks
├── structures-engine/        # Basic stress and loading calculations
└── payload-engine/           # Sensor and optic GSD resolutions
```

Each folder represents a modular Python package with internal subdirectories corresponding to detailed models (e.g. solvers, radiation, conduction, batteries, chemical/electric thrusters, etc.).

## Backward Compatibility
To avoid syntax problems in imports involving hyphens (e.g., `import engines.power-engine`), the root packages are bridged via standard Python wrappers (`power_engine.py`, `orbit_engine.py`, etc.) located directly in the `engines/` root, which are imported by unit tests and REST APIs.
