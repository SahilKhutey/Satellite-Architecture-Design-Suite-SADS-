# SADS Subsystem Reference — Structural Subsystem

**Document ID:** SADS-SUB-STR-001  
**Revision:** 1.0  
**Classification:** Engineering Reference

---

## 1. Overview

The Structural Subsystem defines the mechanical chassis structure, mass distribution, material properties, and launching load capacity limits (e.g. static and dynamic G-loads).

---

## 2. Modeling Principles

### 2.1 Center of Mass (CoM)
Computed by mass-weighted summation over all components:
$$\vec{r}_{\text{CoM}} = \frac{\sum m_i \vec{r}_i}{\sum m_i}$$

### 2.2 Inertia Matrix
Evaluated relative to the center of mass to support ADCS rigid body dynamics:
$$I = \sum m_i \left( (\vec{r}_i \cdot \vec{r}_i) \mathbf{E} - \vec{r}_i \otimes \vec{r}_i \right)$$

---

## 3. Structural Limits
* **Maximum Wet Mass**: $180\text{ kg}$ (ESPA ring launch configuration limit).
* **Fundamental Frequency Limit**: $> 50\text{ Hz}$ axial, $> 30\text{ Hz}$ lateral (typical launch vehicle stiffness requirement).
