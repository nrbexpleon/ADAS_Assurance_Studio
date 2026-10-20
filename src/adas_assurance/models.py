from __future__ import annotations
from dataclasses import asdict, dataclass, field
from math import hypot, isfinite
from typing import Any

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
    def __post_init__(self):
        if not self.object_id or not self.label: raise ValueError("object identity and label required")
        if not all(isfinite(v) for v in (self.x_m,self.y_m,self.vx_mps,self.vy_mps,self.confidence)): raise ValueError("object values must be finite")
        if not 0 <= self.confidence <= 1: raise ValueError("confidence must be 0..1")
    def distance(self, other: "ObjectState") -> float: return hypot(self.x_m-other.x_m,self.y_m-other.y_m)
    def to_dict(self): return asdict(self)

@dataclass(frozen=True, slots=True)
class GroundTruth:
    frame_id: str
    objects: tuple[ObjectState,...]

@dataclass(frozen=True, slots=True)
class Detection:
    frame_id: str
    objects: tuple[ObjectState,...]
    latency_ms: float
    memory_mb: float
    model_version: str
    def __post_init__(self):
        if self.latency_ms < 0 or self.memory_mb < 0 or not self.model_version: raise ValueError("valid latency, memory and model version required")

@dataclass(frozen=True, slots=True)
class SensorObservation:
    sensor: str
    timestamp_ms: int
    objects: tuple[ObjectState,...]
    healthy: bool = True
    def __post_init__(self):
        if not self.sensor or self.timestamp_ms < 0: raise ValueError("sensor and non-negative timestamp required")

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
    metadata: dict[str,Any] = field(default_factory=dict)
    def __post_init__(self):
        if not self.frame_id or self.timestamp_ms < 0 or self.visibility_m < 0 or self.speed_mps < 0: raise ValueError("invalid frame")
        if not all(0 <= x <= 1 for x in (self.map_confidence,self.localization_confidence,self.sensor_health)): raise ValueError("confidence must be 0..1")
