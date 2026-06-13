# Power Simulation Model Reference

## 1. Battery State of Charge (SoC) integration
Battery SoC is bounded and integrated over time steps:
\[SoC(t) = SoC(0) + \int_{0}^{t} \eta_{c} \frac{P_{charge}(\tau) - P_{discharge}(\tau)/(\eta_{d})}{E_{capacity}} d\tau\]

## 2. Load Profiles
Power loads are defined per state (Safe Mode, Science Ops, Communication, Detumble). The simulation steps through the mission timelines, mapping power states to physical battery capacity limits.
