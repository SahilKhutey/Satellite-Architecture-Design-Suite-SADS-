# Thermal Simulation Solver Reference

## 1. Transient Nodal Solver
SADS resolves thermal node temperatures dynamically over time. The integration uses an explicit Euler or implicit backward differentiation formula:
\[T_i(t + \Delta t) = T_i(t) + \frac{\Delta t}{m_i C_p} \left[ Q_{int} + Q_{ext} - Q_{rad} - Q_{cond} \right]\]

## 2. Radiative Flux Integrals
The solver integrates solar flux, Earth albedo, and planetary IR over each time step based on the satellite's face normals:
\[F_{solar} = G_{solar} \cdot \vec{n} \cdot \vec{s}\]
where $\vec{s}$ is the sun vector, and $\vec{n}$ is the face normal vector.
