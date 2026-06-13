# Satellite Architecture Design Suite (SADS)

SADS is a professional, production-grade conceptual aerospace systems engineering platform. It functions as a digital engineering platform, systems planning composer, and mission design environment allowing satellite engineers to visually layout, connect, simulate, and optimize spacecraft subsystems before manufacturing.

---

## 1. Systems Architecture

SADS follows a modular, layer-oriented architecture separating physics/mathematical calculations from the presentation layer:

```
┌──────────────────────────────────────┐
│        SADS HTML5/JS Web Client       │
└──────────────────────────────────────┘
                   │
                   ▼  (REST API / JSON)
┌──────────────────────────────────────┐
│        FastAPI API Service Layer     │
└──────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       Simulation Engine Layer        │
└──────────────────────────────────────┘
 ├── Power Subsystem Engine
 ├── Thermal Subsystem Engine
 ├── Communication Subsystem Engine
 ├── Propulsion Subsystem Engine
 ├── ADCS Subsystem Engine
 └── Orbital Mechanics Engine
```

### Components

1. **Spacecraft Subsystem Engines (`/engines`):** Dataclasses and utility functions containing the math and physics foundations (Keplerian dynamics, Tsiolkovsky rocket equation, Stefan-Boltzmann thermal radiation, link budgets, and rigid body dynamics).
2. **Simulation Service (`/services`):** Integrator service that coordinates simulation timelines across different mission phases.
3. **FastAPI Web Host (`/api/main.py`):** Serves the simulation JSON endpoints and delivers the client static files.
4. **Figma-style Canvas Editor (`/apps/web_client`):** A frontend SPA using Three.js for 3D orbital pathing and assembly model visualization, Chart.js for data plots, and SVG for 2D schema connections.

---

## 2. Mathematical & Physics Foundations

### Power Subsystem
Generates instantaneous array power using:
$$P = \eta \cdot A \cdot G \cdot (1 - \text{degradation})^{\text{years}}$$
Where $G$ is solar flux ($1361\text{ W/m}^2$ LEO AM0), $\eta$ is cell efficiency, and $A$ is array surface area.

Usable battery capacity handles eclipse periods via:
$$\text{Usable Capacity} = \text{Capacity}_{\text{wh}} \cdot \text{DoD}_{\text{limit}}$$

### Thermal Subsystem
Calculates radiation balance for a lumped thermal node using the Stefan-Boltzmann law solved iteratively via Newton-Raphson:
$$Q_{\text{in}} = Q_{\text{solar}} + Q_{\text{albedo}} + Q_{\text{Earth-IR}} + Q_{\text{internal}}$$
$$Q_{\text{out}} = \epsilon \cdot \sigma \cdot A \cdot T^4$$
Solve for equilibrium temperature $T$:
$$T_{n+1} = T_n - \frac{Q_{\text{out}}(T_n) - Q_{\text{in}}}{4 \cdot \epsilon \cdot \sigma \cdot A \cdot T_n^3}$$

### Communications Subsystem
Computes path losses and receiver signal-to-noise ratios via Link Budget equations:
$$L_{fs} = \left(\frac{4\pi d}{\lambda}\right)^2$$
$$\text{EIRP} = P_{tx} + G_{tx} - L_{line}$$
$$\text{CNR} = \text{EIRP} + G_{rx} - L_{fs} - L_{atmos} - 10\log_{10}(k \cdot T_{\text{sys}} \cdot R_{\text{data}})$$

### Propulsion Subsystem
Applies Tsiolkovsky's rocket equation to calculate propellant mass budgets:
$$\Delta V = I_{sp} \cdot g_0 \cdot \ln\left(\frac{m_{\text{wet}}}{m_{\text{dry}}}\right)$$

### ADCS Subsystem
Calculates pointing budgets via sensor RSS error, and checks wheel momentum bounds.

### Orbital Mechanics
Circular orbit period calculations:
$$T_{\text{orbit}} = 2\pi\sqrt{\frac{a^3}{\mu}}$$
Nodal regression RAAN drift due to Earth oblateness ($J_2$ perturbation):
$$\dot{\Omega} = -\frac{3}{2}\frac{n J_2 R_{\text{Earth}}^2}{a^2 (1-e^2)^2}\cos(i)$$

---

## 3. Setup & Running Instructions

### Dependencies

Ensure Python 3.9+ is installed. Install the necessary packages using `pip`:

```bash
pip install fastapi uvicorn pydantic pytest
```

### Running SADS Local Server

Run the FastAPI host from the root directory of the workspace:

```bash
python -m uvicorn api.main:app --reload
```

After startup, open your browser and navigate to:
```
http://localhost:8000
```

### Running Verification Tests

Run the engine math and physics verification tests using `pytest`:

```bash
python -m pytest tests/
```

---

## 4. Usage Instructions

1. **Design Canvas (2D Designer):** Drag-and-drop satellite subsystems (solar panels, batteries, thrusters, tanks, high gain antennas) from the left library onto the canvas. Connect output ports to inputs to represent system distribution channels.
2. **Subsystem details:** Click on any node on the canvas to inspect its variables (e.g. adjust GaAs panel surface area, fuel tank mass, battery depth-of-discharge, or transmitter frequency) in the right sidebar. Budgets update in real-time.
3. **3D Assembly:** Switch to the 3D Satellite Assembly tab to view the procedurally generated structure. Use the **Exploded View** slider to separate external covers and see internal reaction wheels and systems.
4. **Orbital Simulation:** Select LEO, MEO, or GEO target orbits. The Orbit propagation tab will visually display the spacecraft track around Earth and compute eclipse durations, J2 drift, and battery charge cycles.
5. **AI Copilot:** Collapsible panel in the right sidebar. Query the AI regarding mission feasibility, thermal margins, or ask for automatic optimization of panel and battery sizes.
