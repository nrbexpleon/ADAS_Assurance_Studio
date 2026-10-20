from __future__ import annotations

from uuid import uuid4

from .evidence import create_evidence
from .fusion import fuse_observations
from .models import Detection, Frame, GroundTruth, HumanReview, SensorObservation
from .odd import evaluate_odd
from .perception import evaluate_perception
from .scenarios import classify_scenario


def _unique_map(items, name: str):
    result = {}
    for item in items:
        if item.frame_id in result:
            raise ValueError(f"duplicate {name} frame_id {item.frame_id}")
        result[item.frame_id] = item
    return result


class AssuranceStudio:
    def run(
        self,
        frames: list[Frame],
        truths: list[GroundTruth],
        detections: list[Detection],
        observations: list[SensorObservation],
        reviews: list[HumanReview] | None = None,
    ) -> dict:
        if not frames:
            raise ValueError("at least one frame is required")
        frame_by = _unique_map(frames, "frame")
        truth_by = _unique_map(truths, "ground-truth")
        detection_by = _unique_map(detections, "detection")
        if set(frame_by) != set(truth_by):
            missing_truth = sorted(set(frame_by) - set(truth_by))
            unknown_truth = sorted(set(truth_by) - set(frame_by))
            raise ValueError(f"frame/truth mismatch; missing truth={missing_truth}, unknown truth={unknown_truth}")
        unknown_detections = sorted(set(detection_by) - set(frame_by))
        if unknown_detections:
            raise ValueError(f"detections reference unknown frames: {unknown_detections}")

        review_by = _unique_map(reviews or [], "review")
        unknown_reviews = sorted(set(review_by) - set(frame_by))
        if unknown_reviews:
            raise ValueError(f"reviews reference unknown frames: {unknown_reviews}")

        perception = evaluate_perception(truths, detections)
        fusion = fuse_observations(observations)
        odd = [evaluate_odd(frame) for frame in frames]
        scenarios = []
        for frame in frames:
            scenario = classify_scenario(frame.speed_mps, truth_by[frame.frame_id].objects)
            review = review_by.get(frame.frame_id)
            scenarios.append({"frame_id": frame.frame_id, **scenario, "review": review.to_dict() if review else None})

        critical_ids = {item["frame_id"] for item in scenarios if item["risk"] == "critical"}
        approved_critical_ids = {
            frame_id for frame_id, review in review_by.items()
            if review.decision == "approved" and frame_id in critical_ids
        }
        gates = {
            "input_alignment": True,
            "precision": perception["precision"] >= 0.90,
            "recall": perception["recall"] >= 0.90,
            "latency": perception["p95_latency_ms"] <= 100,
            "odd": all(item["state"] == "inside" for item in odd),
            "critical_scenarios_reviewed": critical_ids <= approved_critical_ids,
        }
        report = {
            "run_id": str(uuid4()),
            "schema_version": "1.1",
            "perception": perception,
            "fusion": fusion,
            "odd": odd,
            "scenarios": scenarios,
            "review_summary": {
                "critical_scenarios": len(critical_ids),
                "approved_critical_scenarios": len(approved_critical_ids),
                "submitted_reviews": len(review_by),
            },
            "gates": gates,
            "decision": "eligible-for-human-review" if all(gates.values()) else "investigation-required",
            "human_approval_required": True,
            "disclaimer": "Engineering evidence only; not proof of safety, SOTIF compliance, ASIL compliance, or production readiness.",
        }
        return {**report, "evidence": create_evidence(report)}
