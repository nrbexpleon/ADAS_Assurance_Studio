from __future__ import annotations
from uuid import uuid4
from .evidence import create_evidence
from .fusion import fuse_observations
from .odd import evaluate_odd
from .perception import evaluate_perception
from .scenarios import classify_scenario

class AssuranceStudio:
    def run(self,frames,truths,detections,observations)->dict:
        if not frames:raise ValueError("at least one frame required")
        perception=evaluate_perception(truths,detections);fusion=fuse_observations(observations);odd=[evaluate_odd(x) for x in frames]
        scenarios=[classify_scenario(frame.speed_mps,truth.objects) for frame,truth in zip(frames,truths)]
        gates={"precision":perception["precision"]>=.9,"recall":perception["recall"]>=.9,"latency":perception["p95_latency_ms"]<=100,"odd":all(x["state"]=="inside" for x in odd),"critical_scenarios_reviewed":not any(x["risk"]=="critical" for x in scenarios)}
        report={"run_id":str(uuid4()),"schema_version":"1.0","perception":perception,"fusion":fusion,"odd":odd,"scenarios":scenarios,"gates":gates,"decision":"eligible-for-human-review" if all(gates.values()) else "investigation-required","human_approval_required":True,"disclaimer":"Engineering evidence only; not proof of safety, SOTIF compliance, ASIL compliance, or production readiness."}
        return {**report,"evidence":create_evidence(report)}
