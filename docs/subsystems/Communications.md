# Communications Subsystem Engineering Reference

## 1. Link Budget Equation
The received power-to-noise density ratio $C/N_0$ is given by:
\[\frac{C}{N_0} = EIRP - L_{fs} - L_{atm} + \frac{G_{rx}}{T_{sys}} - k_B\]

Where:
- $EIRP = P_{tx} \cdot G_{tx} \cdot L_{line}$ (Equivalent Isotropically Radiated Power)
- $L_{fs} = 20 \log_{10}\left(\frac{4\pi d}{\lambda}\right)$ (Free Space Path Loss)
- $G_{rx}$ is receiver antenna gain.
- $T_{sys}$ is system noise temperature.
- $k_B$ is Boltzmann's constant ($-228.6 \text{ dBW/Hz-K}$).

## 2. Antenna Gain Formula
For parabolic dishes:
\[G = \eta \cdot \left(\frac{\pi D}{\lambda}\right)^2\]
where $D$ is dish diameter and $\eta$ is aperture efficiency (typically 0.55).
