# Power Subsystem Design & Sizing Reference

## 1. EPS Topology
The SADS EPS simulation assumes a Direct Energy Transfer (DET) or Peak Power Tracking (PPT) topology:
- **Solar Generation:** $P_{gen} = \eta \cdot A \cdot G \cdot \cos(\theta) \cdot L_{degrade}$
- **Battery Storage:** $E_{batt}(t) = E_{batt}(0) + \int (P_{gen}(t) - P_{load}(t)/\eta_{conv}) dt$

## 2. Solar Array Sizing
To size solar panels for a given orbit:
\[A_{panel} = \frac{P_{load} \cdot T_{orbit}}{\eta \cdot G \cdot T_{sun} \cdot \cos(\theta) \cdot L_{degrade}}\]

## 3. Battery Capacity Sizing
To support eclipse loads:
\[C_{batt} = \frac{P_{eclipse} \cdot T_{eclipse}}{DOD \cdot V_{bus} \cdot \eta_{discharge}}\]
Where:
- $DOD$ is the maximum Depth of Discharge (typically 20% to 70% based on cell chemistry).
- $\eta_{discharge}$ is the converter efficiency.
