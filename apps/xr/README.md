# XR Workspace (Unity / WebXR)

This directory contains the Unity assets and WebXR builds for the SADS XR Visualization workspace.

## Platforms Supported
- **Meta Quest 3 / Pro** (via OpenXR + WebXR)
- **Apple Vision Pro** (via Unity PolySpatial / Safari WebXR)
- **Microsoft HoloLens 2** (via MRTK)

## Folder Structure
- `unity/`: Unity project root with MRTK3, OpenXR plugin, and scene layouts.
- `quest/`: Android build outputs.
- `vision_pro/`: VisionOS build outputs.
- `assets/`: 3D meshes, materials, and CAD imports (e.g. GLTF/STEP).

## Integration
The XR client fetches satellite component topologies via the REST/WebSocket gateway service (`/api/simulation/run`) and maps telemetry signals directly to interactive 3D nodes.
