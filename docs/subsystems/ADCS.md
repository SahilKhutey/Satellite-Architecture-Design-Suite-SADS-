# ADCS (Attitude Determination and Control System) Reference

## 1. Spacecraft Attitude Dynamics
Governed by Euler's rotational equation:
\[I \dot{\omega} + \omega \times (I \omega + h_w) = T_{ext} - T_{act}\]

Where:
- $I$ is the inertia tensor of the spacecraft.
- $\omega$ is the angular velocity vector.
- $h_w$ is the angular momentum of the reaction wheels.
- $T_{ext}$ represents external disturbance torques (gravity gradient, magnetic, aerodynamic, solar radiation pressure).
- $T_{act}$ represents actuator command torque.

## 2. Pointing Accuracy Budget
SADS calculates total pointing error from three sources:
\[\theta_{total} = \sqrt{\theta_{sensor}^2 + \theta_{controller}^2 + \theta_{actuator}^2}\]
Ensure this total is less than the payload requirement.
