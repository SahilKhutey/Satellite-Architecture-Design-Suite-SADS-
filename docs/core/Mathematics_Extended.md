# SADS — Mathematics Extended Reference

**Document ID:** SADS-MTH-EXT-001  
**Revision:** 1.0  
**Classification:** Engineering Reference — Mathematical Foundations  
**Pairs with:** `Mathematics.md` (foundational), `Physics.md` (physical), `Engineering.md` (procedural)

---

## 0. Document Purpose

This document provides the **formal mathematical derivations, theorems, and extended formulations** that underpin the SADS engineering engines. It is the companion to the introductory `Mathematics.md` and the source for advanced formulations used in `engines/*.py`.

---

## 1. Linear Algebra — Extended

### 1.1 Vector Spaces for Spacecraft State
The complete state of a spacecraft is represented in a **product space**:

$$\mathbf{x} \in \mathbb{R}^{n_r} \times SO(3) \times \mathbb{R}^{n_w}$$

where:
- $\mathbb{R}^{n_r}$ = position (3) + velocity (3) + auxiliary states
- $SO(3)$ = attitude (special orthogonal group, 3×3 rotation)
- $\mathbb{R}^{n_w}$ = wheel speeds, propellant mass, thermal nodes, etc.

State vectors are partitioned as:
$$\mathbf{x}_{orb} = [r_x, r_y, r_z, v_x, v_y, v_z]^T \in \mathbb{R}^6$$
$$\mathbf{x}_{att} = [q_w, q_x, q_y, q_z, \omega_x, \omega_y, \omega_z]^T \in \mathbb{R}^7$$

### 1.2 Rotation Representations
* **Euler angles (3-1-2 / yaw-pitch-roll sequence):**
  $$R = R_z(\psi) R_y(\theta) R_x(\phi)$$
* **Quaternions (preferred for integration):**
  $$\mathbf{q} = [q_w, q_x, q_y, q_z]$$
  with constraint $|\mathbf{q}| = 1$ to prevent drift.

Conversion quaternion → rotation matrix:
$$R = \begin{bmatrix}
1 - 2(q_y^2 + q_z^2) & 2(q_x q_y - q_w q_z) & 2(q_x q_z + q_w q_y) \\
2(q_x q_y + q_w q_z) & 1 - 2(q_x^2 + q_z^2) & 2(q_y q_z - q_w q_x) \\
2(q_x q_z - q_w q_y) & 2(q_y q_z + q_w q_x) & 1 - 2(q_x^2 + q_y^2)
\end{bmatrix}$$

### 1.3 Inertia Tensor
For a system of point masses $m_i$ at positions $\mathbf{r}_i$ (in body frame, origin at CoM):

$$I = \sum_i m_i \left[(\mathbf{r}_i \cdot \mathbf{r}_i) \mathbb{1} - \mathbf{r}_i \mathbf{r}_i^T\right]$$

Principal values $I_1, I_2, I_3$ are resolved via eigendecomposition:

$$I_{\text{diag}} = R I R^T = \text{diag}(I_1, I_2, I_3)$$

---

## 2. Calculus & Analysis — Extended

### 2.1 Jacobians
For multivariate functions $\mathbf{F}: \mathbb{R}^n \to \mathbb{R}^m$, the Jacobian matrix contains first-order partial derivatives:
$$J_{ij} = \frac{\partial F_i}{\partial x_j}$$

* **SADS Applications:** Newton's solvers for thermal equilibrium and Extended Kalman Filters.

### 2.2 Hessians
$$H_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}$$

* **SADS Applications:** Trust-region methods and second-order optimization.

---

## 3. Differential Equations — Extended

### 3.1 Linear Control Systems
$$\dot{\mathbf{x}} = A \mathbf{x} + B \mathbf{u}$$

State propagation is computed using the matrix exponential:
$$\mathbf{x}(t) = e^{A(t-t_0)} \mathbf{x}(t_0) + \int_{t_0}^t e^{A(t-\tau)} B \mathbf{u}(\tau)\, d\tau$$

### 3.2 Perturbed Keplerian Motion
$$\ddot{\mathbf{r}} = -\frac{\mu}{r^3}\mathbf{r} + \mathbf{a}_{J2} + \mathbf{a}_{drag} + \mathbf{a}_{SRP} + \mathbf{a}_{3rd\_body}$$

---

## 4. Numerical Methods — Extended

### 4.1 Runge-Kutta 4 (RK4)
Used for fixed-step propagation of attitude dynamics and orbital elements:
$$\mathbf{y}_{n+1} = \mathbf{y}_n + \frac{h}{6}(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4)$$

### 4.2 Kepler Equation Solver (Newton-Raphson)
Solve $M = E - e \sin E$ for eccentric anomaly $E$:

$$E_{n+1} = E_n - \frac{E_n - e \sin E_n - M}{1 - e \cos E_n}$$

---

## 5. Probability & Statistics — Extended

### 5.1 Uncertainty Propagation
For uncorrelated input distributions:
$$\sigma_y^2 = \sum_i \left(\frac{\partial f}{\partial x_i}\right)^2 \sigma_{x_i}^2$$

### 5.2 Sobol Sensitivity Analysis
First-order indices describe variance contribution of input $X_i$:
$$S_i = \frac{V[E[Y|X_i]]}{V[Y]}$$

---

## 6. Optimization — Extended

### 6.1 Sequential Quadratic Programming (SQP)
Solves constrained non-linear optimization problems iteratively by approximating the Lagrangian:
$$\min_{\mathbf{d}} \nabla f^T \mathbf{d} + \frac{1}{2} \mathbf{d}^T B \mathbf{d} \quad \text{s.t.} \quad \nabla g_i^T \mathbf{d} + g_i \le 0$$

* **SADS Applications:** Mass minimization and structural payload packing layouts.

---

## 7. Graph Theory for Systems Architecture

Spacecraft wiring and routing are modeled as a typed multigraph $\mathcal{G} = (V, E)$.
* **Nodes ($V$):** Power panels, batteries, components.
* **Edges ($E$):** Power lines, data lines, fuel lines.
* **Flow Optimization:** Max-flow min-cut algorithms determine power routing limits under cable faults.

---

## 8. Computational Complexity Reference

| Algorithm | Domain | Time Complexity | Space Complexity |
|:---|:---|:---|:---|
| RK4 Orbit Step | Orbit Propagation | $O(1)$ | $O(1)$ |
| Kepler Solver | Kepler Mechanics | $O(N_{\text{iterations}})$ | $O(1)$ |
| Newton-Raphson Thermal | Thermal Solver | $O(N_{\text{nodes}}^3)$ | $O(N_{\text{nodes}}^2)$ |
| Dijkstra Route | Cable Harness | $O((V+E)\log V)$ | $O(V+E)$ |
| SQP Optimization | System Optimization | $O(N_{\text{vars}}^3)$ | $O(N_{\text{vars}}^2)$ |
| EKF Filter Step | ADCS Estimation | $O(N_{\text{states}}^3)$ | $O(N_{\text{states}}^2)$ |

---

## 9. References
- Hairer, E., Norsett, S. P., Wanner, G., *Solving Ordinary Differential Equations I*.
- Nocedal, J., Wright, S. J., *Numerical Optimization*.
- West, D. B., *Introduction to Graph Theory*.
