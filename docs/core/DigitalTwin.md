# SADS — Digital Twin Engine

**Document ID:** SADS-DTW-001
**Revision:** 1.0

---

## 1. Digital Twin Concept

SADS generates a **Digital Twin** synchronized with the design state, simulation environment, and operational telemetry. This creates a continuous feedback loop spanning the spacecraft's lifecycle.

---

## 2. Synchronization Architecture

The digital twin uses three synchronization channels:

```
    ┌────────────────────────┐
    │  Operational Satellite │
    └───────────┬────────────┘
                │ CCSDS / MQTT Telemetry
                ▼
    ┌────────────────────────┐
    │     Telemetry Ingest   │
    └───────────┬────────────┘
                │ JSON / Protobuf
                ▼
    ┌────────────────────────┐
    │   Digital Twin Core    │ ◄── Dynamic Design Baseline
    └───────────┬────────────┘
                │ State Comparison
                ▼
    ┌────────────────────────┐
    │  Predictive Analytics  │
    └────────────────────────┘
```

### 2.1 Inbound Telemetry Ingest
SADS ingests physical telemetry packets:
* **CCSDS Space Link Protocol:** Ground station telemetry is parsed into float value channels.
* **MQTT Message Broker:** Ingests local mock telemetry or flat-file operational logs at scale.

---

## 3. Real-Time Analytics & Diagnostics

The digital twin runs active analytics to compare flight measurements against simulation expectations.

### 3.1 Anomaly Detection
Telemetry values are checked against simulation baselines:

$$e_i(t) = |x_{flight, i}(t) - x_{sim, i}(t)|$$

An anomaly is flagged if error $e_i(t)$ exceeds three standard deviations ($3\sigma$) of the calculated system sensor noise covariance:

$$e_i(t) > 3\sqrt{P_{ii}(t)}$$

where $P_{ii}(t)$ is the diagonal variance element from the active Kalman Filter state estimator.

### 3.2 Predictive Degradation Sizing
* **Solar Panel Power EOL Projection:** Measures actual vs expected generation under identical Sun vectors to calculate EOL margins.
* **Battery Capacity fade:** Track discharge curves during eclipses and estimates remaining battery cycles using Coulomb counting:
  $$\text{State of Health (SoH)} = \frac{C_{\text{discharge, current}}}{C_{\text{discharge, nominal}}} \times 100$$
* **Thruster Catalyst Degradation:** Compares cold-gas or monopropellant fuel drawdowns against actual delta-V to flag leak states or nozzle degradation.
