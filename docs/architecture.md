# Architecture and assurance semantics

The studio separates deterministic domain logic from model, simulator, vehicle and storage adapters. Inputs use explicit SI units and immutable records. Each module returns inspectable evidence rather than autonomous control decisions.

## Data integrity

A run requires a non-empty, unique frame catalogue and an exactly aligned ground-truth catalogue. Detection frames must be unique and reference known frames. Missing detections are retained as evidence and counted as false negatives. Reviews must reference known frames and contain a reviewer, rationale and an approved/rejected decision.

These checks prevent Python `zip` truncation, orphan detections and duplicate-frame overwrites from silently changing assurance results.

## Gates

The reference campaign requires:

1. aligned inputs;
2. precision of at least 0.90;
3. recall of at least 0.90;
4. p95 inference latency at most 100 ms;
5. every frame inside the configured ODD; and
6. an approved human review for every critical scenario.

These are demonstration defaults, not universal acceptance criteria. Passing gates produces `eligible-for-human-review`, never an automatic safety or release approval.

## Evidence

The report contains metrics, scenarios, reviews, gate outcomes and a mandatory-human-approval marker. The evidence envelope uses canonical JSON plus SHA-256 to detect accidental or deliberate modification. SHA-256 integrity is not signer identity; production deployments should add KMS/HSM-backed signatures and a governed trust model.

## Service boundary

The standard-library HTTP service:

- binds to loopback by default;
- accepts complete campaign JSON at `POST /api/runs`;
- rejects bodies larger than 1,000,000 bytes;
- supports an optional bearer token;
- retains at most 200 reports in memory;
- optionally persists reports atomically through `REPORT_DIR`; and
- exposes no vehicle-control interface.

Production exposure requires a reverse proxy, TLS, OIDC/RBAC, tenant isolation, rate limiting, centralized audit storage, retention controls and independent cybersecurity review.

## Integration roadmap

1. OpenSCENARIO/OpenDRIVE scenario exchange and deterministic replay.
2. ROS 2 bag, camera, radar, lidar, GNSS and IMU adapters.
3. MOT, mAP, segmentation, calibration, OOD and robustness metrics.
4. Sensor-time alignment, coordinate transforms and covariance-aware EKF/UKF fusion.
5. VehicleTwin Lab fault campaigns and EdgeAI SafetyBench model qualification.
6. HIL, target execution profiling, traceability and independently reviewed safety evidence.
