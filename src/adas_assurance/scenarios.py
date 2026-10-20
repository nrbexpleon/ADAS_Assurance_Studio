from __future__ import annotations
from .models import ObjectState

def time_to_collision(ego_speed_mps:float, lead:ObjectState)->float|None:
    closing=ego_speed_mps-lead.vx_mps
    return lead.x_m/closing if closing>0 and lead.x_m>0 else None

def classify_scenario(ego_speed_mps:float, objects:tuple[ObjectState,...])->dict:
    events=[];minimum=None
    for obj in objects:
        ttc=time_to_collision(ego_speed_mps,obj)
        if ttc is not None: minimum=ttc if minimum is None else min(minimum,ttc)
        if obj.label in {"pedestrian","cyclist"} and 0<obj.x_m<30 and abs(obj.y_m)<3:events.append("vulnerable-road-user-ahead")
        if obj.label in {"car","truck"} and 0<obj.x_m<20 and abs(obj.y_m)<1.8:events.append("close-lead-vehicle")
        if obj.label in {"car","truck"} and abs(obj.y_m)<1 and abs(obj.vy_mps)>1:events.append("cut-in")
    risk="critical" if minimum is not None and minimum<1.5 else "high" if minimum is not None and minimum<3 else "medium" if events else "low"
    return {"events":sorted(set(events)),"minimum_ttc_s":minimum,"risk":risk,"requires_review":risk in {"critical","high"}}
