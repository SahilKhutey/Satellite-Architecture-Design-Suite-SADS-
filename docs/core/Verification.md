# SADS — Verification & Validation

**Document ID:** SADS-VNV-001
**Revision:** 1.0

---

## 1. V&V Framework Overview

SADS incorporates a continuous automated verification and validation pipeline based on **NASA-STD-7009** (Standard for Models and Simulations) and **ECSS-E-ST-10C** (Space Engineering System Engineering). The validation engine runs checks whenever the system design is modified or a simulation is executed.

---

## 2. Automated Subsystem Checks

### 2.1 Power Subsystem Validation
* **Energy Balance Rule:** Total power generated during the sunlit orbital phase must exceed total load energy consumed over the entire orbit, including battery charging efficiency:
  $$E_{\text{generated}} = P_{\text{generation}} \cdot t_{\text{sunlight}} \cdot \eta_{\text{charge}}$$
  $$E_{\text{consumed}} = P_{\text{load, average}} \cdot (t_{\text{sunlight}} + t_{\text{eclipse}})$$
  $$\text{Validation Condition: } E_{\text{generated}} > E_{\text{consumed}}$$
* **Depth of Discharge Margin:** The battery depth of discharge during eclipse must stay below the configured DoD safety limit (typically 30% for LEO GaAs/Li-ion missions to preserve cycle lifetime):
  $$\text{DoD}_{\text{max}} = \frac{P_{\text{load, average}} \cdot t_{\text{eclipse}}}{C_{\text{battery}}} \le \text{DoD}_{\text{limit}}$$

### 2.2 Thermal Subsystem Validation
* **Operating Limit Checks:** Nodal temperatures resolved in simulation must remain within the component's qualification temperature ranges, including a default $10^\circ\text{C}$ engineering margin:
  $$T_{\text{operational, min}} + 10 \le T_{\text{node}} \le T_{\text{operational, max}} - 10$$

### 2.3 Communications Subsystem Validation
* **Link Closure Rule:** The signal-to-noise ratio margin must remain above $3.0\text{ dB}$ (or a user-specified threshold) at the maximum line-of-sight distance between the satellite and the target ground station:
  $$\text{Margin}_{\text{dB}} = \text{CNR}_{\text{achieved}} - \text{CNR}_{\text{required}} \ge 3.0\text{ dB}$$

### 2.4 Propulsion Subsystem Validation
* **Delta-V Margin Rule:** Propellant mass must provide a 10% reserve margin over the sum of all mission maneuver velocity changes:
  $$\Delta V_{\text{available}} \ge 1.10 \cdot \sum \Delta V_{\text{maneuvers}}$$

### 2.5 ADCS Subsystem Validation
* **Slew Torque Margin:** Reaction wheels and magnetorquers must supply torque exceeding the maximum slew acceleration requirements:
  $$\tau_{\text{actuator}} \ge \tau_{\text{slew}} = I \cdot \alpha_{\text{slew}}$$
* **Momentum Desaturation Rule:** Magnetorquers must possess sufficient magnetic dipole moment to dump accumulated angular momentum from environmental disturbances within one orbit period.

---

## 3. Compliance and Standards Verification

SADS automatically builds compliance reports maps to standard aerospace templates:
* **Mass Budget Report:** Verifies total spacecraft wet mass fits launch vehicle adapter payloads (e.g. ESPA rings $<180\text{ kg}$).
* **FMEA Checklist:** Generates failure mode reviews identifying single point failure (SPF) anomalies (e.g. flagging a single solar panel string or a single non-redundant battery pack).
* **Deorbit Compliance:** Computes deorbit timelines from deorbit propulsion delta-V to verify orbital lifetime complies with the 25-year deorbit guideline (IADC-01).
