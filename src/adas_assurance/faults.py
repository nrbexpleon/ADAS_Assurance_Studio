from __future__ import annotations
import random
from dataclasses import replace
from .models import SensorObservation

def inject_fault(observation:SensorObservation, kind:str, magnitude:float=1.0, seed:int=42)->SensorObservation:
    rng=random.Random(seed)
    if magnitude<0:raise ValueError("magnitude must be non-negative")
    if kind=="dropout":return replace(observation,objects=(),healthy=False)
    if kind=="latency":return replace(observation,timestamp_ms=max(0,observation.timestamp_ms-int(magnitude)))
    if kind=="position-bias":return replace(observation,objects=tuple(replace(o,x_m=o.x_m+magnitude,y_m=o.y_m+magnitude/2) for o in observation.objects))
    if kind=="noise":return replace(observation,objects=tuple(replace(o,x_m=o.x_m+rng.gauss(0,magnitude),y_m=o.y_m+rng.gauss(0,magnitude)) for o in observation.objects))
    if kind=="confidence-loss":return replace(observation,objects=tuple(replace(o,confidence=max(0,o.confidence-magnitude)) for o in observation.objects))
    if kind=="freeze":return replace(observation,timestamp_ms=0)
    raise ValueError(f"unsupported fault {kind}")
