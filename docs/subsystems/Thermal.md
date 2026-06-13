# Thermal Subsystem Engineering Reference

## 1. Governing Heat Equation
Spacecraft thermal control relies on radiation and internal conduction:
\[m_i C_{p,i} \frac{dT_i}{dt} = Q_{int,i} + Q_{ext,i} - \sum_{j} R_{r,ij} \sigma (T_i^4 - T_j^4) - \sum_{j} R_{c,ij} (T_i - T_j)\]

Where:
- $Q_{ext,i}$ is the external environmental heat load (solar flux, albedo, Earth IR).
- $R_{r,ij}$ is the radiative coupling.
- $R_{c,ij}$ is the conductive coupling.

## 2. Radiative Coupling
\[R_{r,ij} = \mathcal{F}_{ij} \cdot A_i\]
where $\mathcal{F}_{ij}$ is the radiation exchange factor.

## 3. Passive Control Technologies
- **Multi-Layer Insulation (MLI):** Effective emissivity ($\epsilon^*$) ranges from 0.01 to 0.05.
- **Radiators:** High emissivity ($\epsilon \approx 0.85$), low absorptivity ($\alpha \approx 0.15$) coatings.
