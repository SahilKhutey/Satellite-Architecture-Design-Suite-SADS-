# SADS Simulation Reference — Monte Carlo Methods

**Document ID:** SADS-SIM-MTC-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

To evaluate design reliability and margins under statistical uncertainty, SADS runs Monte Carlo ensembles. 

---

## 2. Parameter Perturbations
We perturb:
* Solar Panel Efficiency: $\eta \sim \mathcal{N}(\eta_{\text{nom}}, \sigma^2)$
* Orbit Altitude: $h \sim \mathcal{N}(h_{\text{nom}}, \sigma^2)$
* Thermal Node Absorbances: $\alpha \sim \mathcal{N}(\alpha_{\text{nom}}, \sigma^2)$
* Fuel Tank Start Capacity: $m_{\text{fuel}} \sim \mathcal{U}(m_{\text{min}}, m_{\text{max}})$

Runs of $1,000$, $10,000$, and $100,000$ simulation samples verify that margins (e.g. power, deorbit fuel) converge with stable standard deviations.
