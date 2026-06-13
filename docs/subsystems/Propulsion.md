# Propulsion Subsystem Engineering Reference

## 1. Tsiolkovsky Rocket Equation
The delta-V ($\Delta V$) capability is calculated from:
\[\Delta V = I_{sp} \cdot g_0 \cdot \ln\left(\frac{m_{start}}{m_{dry}}\right)\]

Where:
- $I_{sp}$ is the specific impulse in seconds.
- $g_0$ is the standard gravitational acceleration ($9.80665 \text{ m/s}^2$).
- $m_{start} = m_{dry} + m_{propellant}$.

## 2. Fuel Depletion & Burn Duration
Burn duration for a constant thrust maneuver:
\[t_{burn} = \frac{m_{propellant} \cdot I_{sp} \cdot g_0}{F_{thrust}}\]
where $F_{thrust}$ is total thruster force (Newtons).
