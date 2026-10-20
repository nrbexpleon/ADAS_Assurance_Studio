from __future__ import annotations

from collections import defaultdict

from .models import Detection, GroundTruth, ObjectState


def match_objects(truth: tuple[ObjectState, ...], detected: tuple[ObjectState, ...], radius_m: float = 2.0):
    if radius_m <= 0:
        raise ValueError("radius_m must be positive")
    candidates = []
    for truth_index, expected in enumerate(truth):
        for detection_index, actual in enumerate(detected):
            distance = expected.distance(actual)
            if expected.label == actual.label and distance <= radius_m:
                candidates.append((distance, truth_index, detection_index))
    matched_truth: set[int] = set()
    matched_detections: set[int] = set()
    pairs = []
    for distance, truth_index, detection_index in sorted(candidates):
        if truth_index not in matched_truth and detection_index not in matched_detections:
            matched_truth.add(truth_index)
            matched_detections.add(detection_index)
            pairs.append((truth[truth_index], detected[detection_index], distance))
    missed = [item for index, item in enumerate(truth) if index not in matched_truth]
    ghosts = [item for index, item in enumerate(detected) if index not in matched_detections]
    return pairs, missed, ghosts


def _unique_by_frame(items, kind: str):
    result = {}
    for item in items:
        if item.frame_id in result:
            raise ValueError(f"duplicate {kind} frame_id {item.frame_id}")
        result[item.frame_id] = item
    return result


def evaluate_perception(truths: list[GroundTruth], detections: list[Detection], radius_m: float = 2.0) -> dict:
    if not truths:
        raise ValueError("at least one ground-truth frame is required")
    truth_by = _unique_by_frame(truths, "ground-truth")
    detection_by = _unique_by_frame(detections, "detection")
    unknown = sorted(set(detection_by) - set(truth_by))
    if unknown:
        raise ValueError(f"detections have no ground truth: {', '.join(unknown)}")

    totals = {"tp": 0, "fp": 0, "fn": 0}
    errors: list[float] = []
    latencies: list[float] = []
    memories: list[float] = []
    by_class = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    missing_frames = []

    for frame_id, truth in truth_by.items():
        detection = detection_by.get(frame_id)
        if detection is None:
            pairs, missed, ghosts = [], list(truth.objects), []
            missing_frames.append(frame_id)
        else:
            pairs, missed, ghosts = match_objects(truth.objects, detection.objects, radius_m)
            latencies.append(detection.latency_ms)
            memories.append(detection.memory_mb)
        totals["tp"] += len(pairs)
        totals["fn"] += len(missed)
        totals["fp"] += len(ghosts)
        errors.extend(pair[2] for pair in pairs)
        for expected, _, _ in pairs:
            by_class[expected.label]["tp"] += 1
        for item in missed:
            by_class[item.label]["fn"] += 1
        for item in ghosts:
            by_class[item.label]["fp"] += 1

    precision = _ratio(totals["tp"], totals["tp"] + totals["fp"])
    recall = _ratio(totals["tp"], totals["tp"] + totals["fn"])
    class_metrics = {}
    for label, counts in sorted(by_class.items()):
        class_precision = _ratio(counts["tp"], counts["tp"] + counts["fp"])
        class_recall = _ratio(counts["tp"], counts["tp"] + counts["fn"])
        class_metrics[label] = {**counts, "precision": class_precision, "recall": class_recall, "f1": _f1(class_precision, class_recall)}
    return {
        "frame_count": len(truths),
        "evaluated_detection_frames": len(detections),
        "missing_detection_frames": sorted(missing_frames),
        "true_positives": totals["tp"],
        "false_positives": totals["fp"],
        "false_negatives": totals["fn"],
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        "mean_position_error_m": sum(errors) / len(errors) if errors else 0.0,
        "p95_latency_ms": percentile(latencies, 0.95),
        "peak_memory_mb": max(memories, default=0.0),
        "by_class": class_metrics,
    }


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def percentile(values: list[float], quantile: float) -> float:
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be 0..1")
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * quantile + 0.999999)))
    return ordered[index]
