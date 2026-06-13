# SADS — Physics Reference Companion

**Document ID:** SADS-PHY-REF-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

This document accompanies `Physics.md` and provides **deep technical reference data**, derivations, coordinate frames, and engineering constants used by SADS engines.

---

## 1. Fundamental Physical Constants (CODATA 2018)

| Constant | Symbol | Value | Units | Relative Uncertainty |
|----------|--------|-------|-------|---------------------|
| Speed of light | $c$ | 299,792,458 | m/s | exact |
| Gravitational constant | $G$ | 6.67430 × 10⁻¹¹ | m³/kg/s² | 2.2 × 10⁻⁵ |
| Standard gravity | $g_0$ | 9.80665 | m/s² | exact |
| Boltzmann constant | $k$ | 1.380649 × 10⁻²³ | J/K | exact |
| Stefan-Boltzmann | $\sigma$ | 5.670374419 × 10⁻⁸ | W/m²/K⁴ | exact |
| Planck constant | $h$ | 6.62607015 × 10⁻³⁴ | J·s | exact |
| Avogadro number | $N_A$ | 6.02214076 × 10²³ | /mol | exact |
| Universal gas constant | $R$ | 8.31446 | J/mol/K | exact |
| Elementary charge | $e$ | 1.602176634 × 10⁻⁹ | C | exact |
| Vacuum permittivity | $\varepsilon_0$ | 8.8541878128 × 10⁻¹² | F/m | 1.5 × 10⁻¹⁰ |
| Vacuum permeability | $\mu_0$ | 1.25663706212 × 10⁻⁶ | N/A² | exact |
| Astronomical unit | AU | 149,597,870,700 | m | exact (def.) |

---

## 2. Solar System Bodies

| Body | μ [m³/s²] | R [km] | T [s] | Obliquity | J2 |
|------|-----------|--------|-------|-----------|-----|
| Sun | 1.32712440018 × 10²⁰ | 695,700 | — | — | — |
| Mercury | 2.2032 × 10¹³ | 2,439.7 | 5.0674 × 10⁶ | 0.034° | 6 × 10⁻⁵ |
| Venus | 3.24859 × 10¹⁴ | 6,051.8 | 1.9414 × 10⁷ | 177.4° | 4.46 × 10⁻⁶ |
| Earth | 3.986004418 × 10¹⁴ | 6,378.137 | 86,164.0905 | 23.4393° | 1.08263 × 10⁻³ |
| Moon | 4.9048695 × 10¹² | 1,737.4 | 2.3606 × 10⁶ | 6.68° | 2.03 × 10⁻⁴ |
| Mars | 4.282837 × 10¹³ | 3,389.5 | 8.8642 × 10⁴ | 25.19° | 1.96 × 10⁻³ |
| Jupiter | 1.2668653 × 10¹⁷ | 69,911 | 35,530 | 3.13° | 1.4736 × 10⁻² |
| Saturn | 3.7940588 × 10¹⁶ | 58,232 | 37,930 | 26.73° | 1.646 × 10⁻² |

---

## 3. Solar Radiation at 1 AU

| Quantity | Value |
|----------|-------|
| Total irradiance (solar constant) | 1,361 W/m² |
| Photon flux (visible) | ~1.5 × 10²¹ /m²/s |
| Spectral peak | 0.48 μm |
| Photon pressure | 4.56 μN/m² |

---

## 4. Atmosphere (Earth, NRLMSISE-00 representative)

| Altitude [km] | Density [kg/m³] | T [K] | Pressure [Pa] |
|---------------|-----------------|-------|---------------|
| 0 | 1.225 | 288 | 101,325 |
| 100 | 5.6 × 10⁻⁷ | 195 | 3.2 × 10⁻² |
| 200 | 2.5 × 10⁻¹⁰ | 855 | 8.5 × 10⁻⁵ |
| 400 | 2.8 × 10⁻¹² | 1000 | 1.5 × 10⁻⁶ |
| 800 | 1.0 × 10⁻¹⁴ | 1000 | 1.0 × 10⁻⁸ |

---

## 5. Typical Satellite Materials Data

| Material | ρ [kg/m³] | E [GPa] | σ_y [MPa] | k [W/m/K] | c_p [J/kg/K] | CTE [1e-6/K] |
|----------|-----------|---------|-----------|-----------|--------------|---------------|
| Al 6061-T6 | 2700 | 69 | 276 | 167 | 900 | 23.6 |
| Al 7075-T6 | 2810 | 72 | 503 | 130 | 960 | 23.4 |
| Ti 6Al-4V | 4430 | 114 | 880 | 6.7 | 526 | 8.6 |
| CFRP (UD, 0°) | 1600 | 140 | 1500 | 5 | 800 | -0.5 (axial) |
| Kapton HN | 1420 | 2.5 | 70 | 0.12 | 1090 | 20 |
| Cu C110 | 8960 | 110 | 220 | 401 | 385 | 17 |
| SS 304 | 8000 | 200 | 215 | 16 | 500 | 17 |

---

## 6. Thermo-Optical Properties (Space-Relevant Surfaces)

| Surface | α (solar) | ε (IR) | α/ε | Use |
|---------|-----------|--------|-----|-----|
| Bare aluminum | 0.20 | 0.04 | 5.0 | Internal |
| White paint (Z-93) | 0.15 | 0.91 | 0.16 | Radiator (warm) |
| Black paint (Z-306) | 0.96 | 0.88 | 1.09 | Cold-biased |
| OSR (2nd surface mirror) | 0.10 | 0.80 | 0.13 | Cold radiator |
| Silver Teflon (FEP) | 0.08 | 0.78 | 0.10 | MLI outer layer |

---

## 7. Battery Energy Density Comparison

| Chemistry | Energy [Wh/kg] | Energy [Wh/L] | Cycle Life | Notes |
|-----------|----------------|---------------|------------|-------|
| Li-ion (NMC) | 150–220 | 250–400 | 500–2000 | Standard |
| Li-ion (LFP) | 90–160 | 200–300 | 2000–5000 | Safer, lower density |
| NiH2 | 50–75 | 60–110 | 1000s | Heritage GEO |

---

## 8. Solar Cell Comparison

| Technology | η (BOL) | η (EOL, 15 yr GEO) | $/W | TRL |
|------------|---------|---------------------|-----|-----|
| Si (mono) | 22% | 16% | 0.5 | 9 |
| GaInP/GaAs/Ge (TJ) | 30% | 24% | 1.5 | 9 |
| 4-junction IMM | 33% | 27% | 3.0 | 8 |

---

## 9. Propulsion Performance

### 9.1 Chemical Propellants

| Propellant | Isp [s] | T_c [K] | Density [kg/L] | Storage |
|------------|---------|---------|----------------|---------|
| Hydrazine (N₂H₄) | 230 | 1100 | 1.01 | Liquid |
| MON-3 (N₂O₄) | 280 | 3000 | 1.45 | Liquid |
| LOX/LH₂ | 450 | 3500 | 0.35 (LOX) + 0.07 (LH₂) | Cryogenic |

### 9.2 Electric Propulsion

| Type | Isp [s] | Thrust [mN] | P [kW] | η_thrust | TRL |
|------|---------|-------------|--------|----------|-----|
| SPT-100 (Hall) | 1600 | 80 | 1.35 | 0.50 | 9 |
| NEXT (ion) | 4190 | 236 | 6.9 | 0.71 | 9 |

---

## 10. ADCS Sensors & Actuators

| Actuator | Torque [N·m] | Momentum [N·m·s] | Mass [kg] | Power [W] |
|----------|--------------|------------------|-----------|-----------|
| Reaction wheel (small) | 0.01 | 0.04 | 0.8 | 5 |
| Reaction wheel (medium) | 0.03 | 0.10 | 1.5 | 10 |
| Magnetorquer (small) | 1e-4 | — | 0.1 | 0.5 |

---

## 11. Common Frequency Allocations

| Band | Frequency Range | Spacecraft Use | Notes |
|------|-----------------|----------------|-------|
| UHF | 300 - 1000 MHz | Amateur, CubeSat TT&C | High path loss margin, low bandwidth |
| S-Band | 2 - 4 GHz | Standard satellite TT&C | Moderate gain, highly reliable |
| X-Band | 8 - 12 GHz | Earth Observation Downlinks | High bandwidth, directional antennas |
| Ka-Band | 26.5 - 40 GHz | High-throughput Comms (GEO) | Rain attenuation sensitive |

---

## 12. Coordinate Reference Frames

Spacecraft analysis requires transforming coordinates between different reference systems:

* **Earth-Centered Inertial (ECI):** Non-rotating frame. Center of Earth origin. X-axis points to vernal equinox, Z-axis points along Earth's rotation axis. Used for orbit propagation.
* **Earth-Centered Earth-Fixed (ECEF):** Earth-rotating frame. Center of Earth origin. X-axis points to prime meridian ($0^\circ$ longitude). Used for ground tracks and coverage analysis.
* **Local Vertical Local Horizontal (LVLH):** Spacecraft-fixed relative frame. Z-axis points nadir (down), Y-axis points along negative orbit normal, X-axis points along velocity vector. Used for pointing control.
* **Spacecraft Body Frame ($X_B, Y_B, Z_B$):** Origin at spacecraft center of mass. Principal axes defined by structural alignment. Used for sensor mounting and actuator torque distribution.

---

## 13. Standard Orbits Reference

* **International Space Station (ISS LEO):** $Altitude \approx 420\text{ km}$, $Inclination \approx 51.6^\circ$, $Period \approx 92.8\text{ min}$.
* **Sun-Synchronous LEO:** $Altitude \approx 600 - 800\text{ km}$, $Inclination \approx 98^\circ$ (depends on altitude). Right ascension precesses at Earth orbital rate ($360^\circ / year$) to maintain constant local solar time.
* **GPS MEO:** $Altitude \approx 20,200\text{ km}$, $Inclination \approx 55^\circ$, $Period \approx 12\text{ hours}$ (semi-synchronous).
* **Geostationary (GEO):** $Altitude \approx 35,786\text{ km}$, $Inclination \approx 0^\circ$, $Period \approx 23.93\text{ hours}$ (sidereal day). Spacecraft stays stationary relative to Earth surface.

---

## 14. Derived Engineering Formulas

### 14.1 Nodal Thermal Radiator Area

To reject internal heat $Q_{int}$ in space:

$$A_{\text{rad}} = \frac{Q_{int}}{\epsilon \sigma T^4}$$

### 14.2 Parabolic Dish Directivity

Beamwidth ($\theta_{3dB}$) and gain relationship:

$$G \approx \frac{41000}{\theta_{3dB, az} \cdot \theta_{3dB, el}} \cdot \eta_{\text{aperture}}$$

---

## 15. Worked Engineering Examples

### 15.1 LEO to GEO Hohmann Transfer Delta-V
Calculate the total velocity change required to transfer from a $300\text{ km}$ LEO altitude circular orbit to $35,786\text{ km}$ GEO (ignoring plane change):

1. **Calculate radii:**
   * $r_1 = 6378.137 + 300 = 6678.137\text{ km}$
   * $r_2 = 6378.137 + 35786 = 42164.137\text{ km}$
2. **First Burn (LEO Exit):**
   $$\Delta v_1 = \sqrt{\frac{\mu}{r_1}} \left( \sqrt{\frac{2 r_2}{r_1 + r_2}} - 1 \right) \approx 7.726 \cdot (1.314 - 1) \approx 2.42\text{ km/s}$$
3. **Second Burn (GEO Insertion):**
   $$\Delta v_2 = \sqrt{\frac{\mu}{r_2}} \left( 1 - \sqrt{\frac{2 r_1}{r_1 + r_2}} \right) \approx 3.075 \cdot (1 - 0.523) \approx 1.47\text{ km/s}$$
4. **Total Delta-V:**
   $$\Delta V_{\text{total}} = 2.42 + 1.47 = 3.89\text{ km/s}$$
