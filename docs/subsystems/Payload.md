# Spacecraft Payload Reference

## 1. Optical Imaging Payloads
Ground Sample Distance (GSD) represents the pixel resolution:
\[GSD = \frac{p \cdot H}{f}\]

Aperture diffraction limit (Rayleigh Criterion):
\[\theta_{res} = 1.22 \frac{\lambda}{D}\]
Where:
- $p$ is sensor pixel pitch.
- $H$ is satellite altitude.
- $f$ is camera focal length.
- $D$ is aperture diameter.
- $\lambda$ is operating wavelength.

## 2. SAR (Synthetic Aperture Radar) Payloads
Minimum antenna area constraint to avoid ambiguities:
\[A_{ant} \ge \frac{4 v_s \cdot H \cdot \tan(\theta_{inc})}{c}\]
Where $v_s$ is satellite velocity, $\theta_{inc}$ is incidence angle, and $c$ is speed of light.
