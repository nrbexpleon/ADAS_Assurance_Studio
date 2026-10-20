from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import hypot, isfinite
from typing import Any


def _require_finite(name: str, *values: float) -> None:
    if not all(isfinite(value) for value in values):
        raise ValueError(f"{name} values must be finite")


@dataclass(frozen=True, slots=True)
class ObjectState:
    object_id: str
    label: str
    x_m: float
    y_m: float
    vx_mps: float = 0.0
    vy_mps: float = 0.0
    confidence: float = 1.0
    source: str = "ground-truth"

    def __post_init__(self) -> None:
        if not self.object_id or not self.label or not self.source:
            raise ValueError("object identity, label and source are required")
        _require_finite("object", self.x_m, self.y_m, self.vx_mps, self.vy_mps, self.confidence)
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be 0..1")

    def distance(self, other: "ObjectState") -> float:
        return hypot(self.x_m - other.x_m, self.y_m - other.y_m)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_objects(objects: tuple[ObjectState, ...]) -> None:
    identifiers = [obj.object_id for obj in objects]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("object identifiers must be unique within a frame")


@dataclass(frozen=True, slots=True)
class GroundTruth:
    frame_id: str
    objects: tuple[ObjectState, ...]

    def __post_init__(self) -> None:
        if not self.frame_id:
            raise ValueError("frame_id is required")
        _validate_objects(self.objects)


@dataclass(frozen=True, slots=True)
class Detection:
    frame_id: str
    objects: tuple[ObjectState, ...]
    latency_ms: float
    memory_mb: float
    model_version: str

    def __post_init__(self) -> None:
        if not self.frame_id or not self.model_version:
            raise ValueError("frame_id and model_version are required")
        _require_finite("detection", self.latency_ms, self.memory_mb)
        if self.latency_ms < 0 or self.memory_mb < 0:
            raise ValueError("latency and memory must be non-negative")
        _validate_objects(self.objects)


@dataclass(frozen=True, slots=True)
class SensorObservation:
    sensor: str
    timestamp_ms: int
    objects: tuple[ObjectState, ...]
    healthy: bool = True

    def __post_init__(self) -> None:
        if not self.sensor or self.timestamp_ms < 0:
            raise ValueError("sensor and non-negative timestamp are required")
        _validate_objects(self.objects)


@dataclass(frozen=True, slots=True)
class Frame:
    frame_id: str
    timestamp_ms: int
    weather: str
    illumination: str
    road_type: str
    visibility_m: float
    speed_mps: float
    map_confidence: float
    localization_confidence: float
    sensor_health: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.frame_id or not self.weather or not self.illumination or not self.road_type or self.timestamp_ms < 0:
            raise ValueError("frame identity, context and timestamp are required")
        _require_finite("frame", self.visibility_m, self.speed_mps, self.map_confidence, self.localization_confidence, self.sensor_health)
        if self.visibility_m < 0 or self.speed_mps < 0:
            raise ValueError("visibility and speed must be non-negative")
        if not all(0 <= value <= 1 for value in (self.map_confidence, self.localization_confidence, self.sensor_health)):
            raise ValueError("confidence must be 0..1")


@dataclass(frozen=True, slots=True)
class HumanReview:
    frame_id: str
    reviewer: str
    decision: str
    rationale: str
    reviewed_at: str = ""

    def __post_init__(self) -> None:
        if not self.frame_id or not self.reviewer or not self.rationale:
            raise ValueError("review target, reviewer and rationale are required")
        if self.decision not in {"approved", "rejected"}:
            raise ValueError("review decision must be approved or rejected")

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
