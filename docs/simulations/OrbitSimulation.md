# Orbit Simulation Model Reference

## 1. Keplerian Dynamics
SADS orbit engine propagates Keplerian state vectors using:
- semi-major axis $a$
- eccentricity $e$
- inclination $i$
- right ascension of ascending node (RAAN) $\Omega$
- argument of perigee $\omega$
- mean anomaly $M$

Orbital Period:
\[T_{period} = 2\pi \sqrt{\frac{a^3}{\mu}}\]

## 2. Environmental Perturbations
- **J2 Oblateness Effect:** Regressions in RAAN ($\dot{\Omega}$) and argument of perigee ($\dot{\omega}$):
\[\dot{\Omega} = -\frac{3}{2} J_2 \left(\frac{R_E}{p}\right)^2 n \cos(i)\]
where $p = a(1-e^2)$.
