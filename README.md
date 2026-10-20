# ADAS Assurance Studio

A dependency-free Python 3.11+ engineering workbench that combines perception qualification, deterministic multi-sensor fusion, sensor fault injection, operational-design-domain monitoring, critical-scenario classification and SHA-256 evidence.

> **Assurance aid—not a vehicle controller.** Results require qualified human review. The project does not prove safety, establish ISO 26262/SOTIF compliance, determine ASIL, replace target/HIL validation or directly actuate a vehicle.

## Implemented

- Object matching and class-level precision/recall/F1
- Position error, p95 latency and peak-memory metrics
- Confidence-weighted camera/radar/lidar-style object fusion
- Timestamp and health rejection with explainable source provenance
- Dropout, latency, position-bias, noise, confidence-loss and freeze faults
- ODD policy for weather, illumination, road, visibility, speed, map, localization and sensor health
- TTC, cut-in, close-lead and vulnerable-road-user scenario classification
- Transparent assurance gates and mandatory human approval
- Canonical SHA-256 evidence verification
- Deterministic campaign generator, CLI, bounded REST API and dashboard
- Dependency-free tests, CodeQL, dependency review and Dependabot

## Quick start

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m adas_assurance.cli --frames 100 --output report.json
PYTHONPATH=src python -m adas_assurance.server
```

Open <http://127.0.0.1:8080>.

## Architecture

```text
Ground truth + detections -> PerceptionGuard metrics ---+
Camera/radar/lidar -------> FusionForge --------------+--> Gates --> Evidence
Sensor streams -----------> FaultStorm ---------------+
Driving context ----------> ODD Sentinel -------------+
Object trajectories ------> ScenarioMine -------------+
```

All units are explicit: metres, metres/second, milliseconds and megabytes. Model runtimes and vehicle/simulator integrations belong behind adapters in future versions.

## Production gaps

Target calibration, time synchronization, sensor models, camera geometry, tracking metrics, datasets, ML runtimes, ROS 2, OpenSCENARIO, HIL, vehicle networks, RBAC, durable storage, KMS signing, independent safety assessment and target performance evidence are not implemented.

## Licence

Current and future versions are proprietary source-available software. Commercial, production, customer, vehicle, embedded-system or field use requires a separate written agreement. Earlier MIT versions retain their historical grant. See `LICENSE`.
