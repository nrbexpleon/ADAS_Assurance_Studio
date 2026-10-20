# Architecture and assurance semantics

The studio separates deterministic domain logic from future model, simulator, vehicle and storage adapters. Inputs use SI units and immutable records. Each module returns inspectable evidence rather than autonomous control decisions.

## Gates

The reference campaign requires precision and recall of at least 0.90, p95 inference latency at most 100 ms, every frame inside the configured ODD, and no unreviewed critical scenario. These are demonstration defaults, not universal acceptance criteria.

## Integration roadmap

1. OpenSCENARIO/OpenDRIVE scenario exchange and deterministic replay.
2. ROS 2 bag, camera, radar, lidar, GNSS and IMU adapters.
3. MOT, mAP, segmentation, calibration, OOD and robustness metrics.
4. Sensor-time alignment, coordinate transforms and covariance-aware EKF/UKF fusion.
5. VehicleTwin Lab fault campaigns and EdgeAI SafetyBench model qualification.
6. HIL, target execution profiling, traceability and independently reviewed safety evidence.
