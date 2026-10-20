from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import Detection, Frame, GroundTruth, HumanReview, ObjectState, SensorObservation


def _objects(values: list[dict[str, Any]]) -> tuple[ObjectState, ...]:
    return tuple(ObjectState(**value) for value in values)


def campaign_from_dict(payload: dict[str, Any]):
    required = {"frames", "truths", "detections", "observations"}
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"campaign is missing fields: {', '.join(missing)}")
    frames = [Frame(**value) for value in payload["frames"]]
    truths = [GroundTruth(value["frame_id"], _objects(value.get("objects", []))) for value in payload["truths"]]
    detections = [
        Detection(value["frame_id"], _objects(value.get("objects", [])), value["latency_ms"], value["memory_mb"], value["model_version"])
        for value in payload["detections"]
    ]
    observations = [
        SensorObservation(value["sensor"], value["timestamp_ms"], _objects(value.get("objects", [])), value.get("healthy", True))
        for value in payload["observations"]
    ]
    reviews = [HumanReview(**value) for value in payload.get("reviews", [])]
    return frames, truths, detections, observations, reviews


def campaign_to_dict(frames, truths, detections, observations, reviews=None) -> dict[str, Any]:
    return {
        "frames": [asdict(value) for value in frames],
        "truths": [asdict(value) for value in truths],
        "detections": [asdict(value) for value in detections],
        "observations": [asdict(value) for value in observations],
        "reviews": [asdict(value) for value in reviews or []],
    }


def load_campaign(path: str | Path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("campaign root must be an object")
    return campaign_from_dict(payload)


def save_campaign(path: str | Path, campaign) -> None:
    frames, truths, detections, observations, *rest = campaign
    reviews = rest[0] if rest else []
    payload = campaign_to_dict(frames, truths, detections, observations, reviews)
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
