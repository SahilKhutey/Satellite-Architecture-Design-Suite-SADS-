# SADS SDK Reference

## 1. Subsystem Modules

SADS can be imported directly as a Python library:

```python
from engines.orbit_engine import circular_orbit
from engines.power_engine import SolarArray, Battery, PowerBudget

# Configure Orbit
orb = circular_orbit(400)
period = orb.orbital_period_s()

# Sizing EPS
array = SolarArray(name="Panel-1", area=2.0, efficiency=0.30)
battery = Battery(name="Pack-1", capacity_wh=100)
```
Refer to [docs/core/API.md](file:///c:/Users/User/Documents/Sattelite%20Architecure%20Design/docs/core/API.md) for REST and GraphQL API routes.
