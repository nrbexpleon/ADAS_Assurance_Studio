# ADAS Assurance Studio

A dependency-free Python 3.11+ engineering workbench for repeatable ADAS perception qualification, deterministic multi-sensor fusion, sensor fault injection, operational-design-domain monitoring, critical-scenario classification, human review and SHA-256 evidence.

> **Assurance aid—not a vehicle controller.** Results require qualified human review. The project does not prove safety, establish ISO 26262/SOTIF compliance, determine ASIL, replace target/HIL validation or directly actuate a vehicle.

## What 0.2.0 adds

- Real campaign ingestion from JSON instead of synthetic data only
- Strict frame, truth, detection, object and review alignment validation
- Missing detection frames counted as false negatives
- Per-class precision, recall and F1 metrics
- Explicit approved/rejected human reviews for critical scenarios
- A bounded REST API for campaign execution, report retrieval and evidence verification
- Optional filesystem-backed report persistence
- Safe DOM rendering in the browser dashboard
- Expanded unit, integration, CLI, persistence and HTTP API tests

## Implemented

- Object matching and class-level precision/recall/F1
- Position error, p95 latency and peak-memory metrics
- Confidence-weighted camera/radar/lidar-style object fusion
- Timestamp and health rejection with explainable source provenance
- Dropout, latency, position-bias, noise, confidence-loss and freeze faults
- ODD policy for weather, illumination, road, visibility, speed, map, localization and sensor health
- TTC, cut-in, close-lead and vulnerable-road-user scenario classification
- Transparent assurance gates and explicit human review records
- Canonical SHA-256 evidence creation and verification
- Deterministic campaign generator, CLI, bounded REST API and dashboard
- Dependency-free tests, CodeQL, dependency review and Dependabot

## Quick start

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m adas_assurance.cli --frames 100 --output report.json
PYTHONPATH=src python -m adas_assurance.cli --write-example campaign.json
PYTHONPATH=src python -m adas_assurance.cli --input campaign.json --output report.json
PYTHONPATH=src python -m adas_assurance.server
```

Open <http://127.0.0.1:8080>.

## Campaign JSON workflow

Generate a documented, valid starting point:

```bash
PYTHONPATH=src python -m adas_assurance.cli --frames 20 --write-example campaign.json
```

Edit `campaign.json` or generate it from your data adapter. The root contains:

- `frames`: driving context and ODD attributes keyed by `frame_id`
- `truths`: reference objects for each frame
- `detections`: model outputs, latency, memory and model version
- `observations`: timestamped camera/radar/lidar-style observations
- `reviews`: optional human decisions for critical frames

Every frame must have matching ground truth. Missing detection frames are allowed and are counted as false negatives. Unknown or duplicate frame IDs are rejected rather than silently truncated.

A review record has this form:

```json
{
  "frame_id": "frame-17",
  "reviewer": "safety.engineer",
  "decision": "approved",
  "rationale": "Trace, labels and timing evidence reviewed",
  "reviewed_at": "2026-10-20T13:00:00Z"
}
```

Only `approved` or `rejected` is accepted. A critical-scenario gate passes only when every critical frame has an approved review. Overall human approval remains mandatory.

## REST API

Start the service with optional controls:

```bash
API_TOKEN='replace-me' REPORT_DIR='./reports' PYTHONPATH=src \
  python -m adas_assurance.server
```

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health and version |
| `POST` | `/api/runs` | Execute a full campaign JSON document |
| `POST` | `/api/runs` | Execute a demo using `{"demo":{"frames":100,"seed":42}}` |
| `GET` | `/api/reports/{run_id}` | Retrieve a stored report |
| `POST` | `/api/verify` | Verify an evidence document |

When `API_TOKEN` is set, send `Authorization: Bearer <token>`. Request bodies are limited to 1,000,000 bytes. In-memory storage retains the newest 200 reports; `REPORT_DIR` additionally enables atomic filesystem persistence.

Example:

```bash
curl -sS -X POST http://127.0.0.1:8080/api/runs \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer replace-me' \
  --data-binary @campaign.json > report.json
```

## Architecture

```text
Ground truth + detections -> PerceptionGuard metrics ---+
Camera/radar/lidar -------> FusionForge --------------+
Sensor streams -----------> FaultStorm ---------------+--> Gates --> Evidence
Driving context ----------> ODD Sentinel -------------+
Object trajectories ------> ScenarioMine ------------+
Human review records ---------------------------------+
```

All units are explicit: metres, metres/second, milliseconds and megabytes. Model runtimes and vehicle/simulator integrations belong behind adapters.

## Production gaps

Target calibration, time synchronization, sensor models, camera geometry, tracking metrics, production datasets, ML runtimes, ROS 2, OpenSCENARIO, HIL, vehicle networks, OIDC/RBAC, database storage, KMS signing, independent safety assessment and target performance evidence remain integration work. See `docs/architecture.md`.

## Licence

Current and future versions are proprietary source-available software. Commercial, production, customer, vehicle, embedded-system or field use requires a separate written agreement. Earlier MIT versions retain their historical grant. See `LICENSE`.
