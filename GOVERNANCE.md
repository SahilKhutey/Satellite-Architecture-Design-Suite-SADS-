# SADS Project Governance

## 1. Project Roles

To ensure SADS operates with the rigor required for aerospace digital engineering, the project defines the following structure:

### Founder / Chief Architect
* Holds final decision-making authority on core system design, mathematics, and physics solvers.

### Core Engineering Team
* Responsible for broad codebase health, deployment configurations, and library management.

### Subsystem Maintainers
* Dedicated experts leading individual spacecraft engineering areas:
  * **Power Lead**: Sizing, battery, and solar panel modeling.
  * **Thermal Lead**: Nodal network heat solvers and radiation models.
  * **Communications Lead**: RF propagation and link budget verification.
  * **Propulsion Lead**: Delta-V and burn planning.
  * **ADCS Lead**: Quaternions, star tracker estimation, and attitude dynamics.
  * **Orbit Lead**: Kepler/Cowell propagators and orbit calculations.
  * **Digital Twin Lead**: Telemetry ingestion and Kalman synchronizers.
  * **AI Lead**: SADS Copilot APIs and aerospace RAG verification.

---

## 2. Decision Making Process

Subsystem modifications require:
1. Physics review by the corresponding Subsystem Lead.
2. Code review and verification gate pass via CI/CD.
3. Final sign-off by the Chief Architect or designated Maintainer.
