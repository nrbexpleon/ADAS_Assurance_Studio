from __future__ import annotations
from .models import ObjectState, SensorObservation

def fuse_observations(observations:list[SensorObservation], timestamp_tolerance_ms:int=100, association_radius_m:float=3.0)->dict:
    if not observations:return {"timestamp_ms":0,"objects":[],"rejected_sensors":[]}
    target=max(x.timestamp_ms for x in observations);accepted=[];rejected=[]
    for observation in observations:
        if not observation.healthy or target-observation.timestamp_ms>timestamp_tolerance_ms: rejected.append(observation.sensor)
        else: accepted.extend((observation.sensor,obj) for obj in observation.objects)
    groups=[]
    for sensor,obj in sorted(accepted,key=lambda x:(x[1].label,x[1].x_m,x[0])):
        group=next((g for g in groups if g[0][1].label==obj.label and g[0][1].distance(obj)<=association_radius_m),None)
        (group if group is not None else groups.append([]) or groups[-1]).append((sensor,obj))
    fused=[]
    for index,group in enumerate(groups):
        weights=[max(.01,obj.confidence) for _,obj in group];total=sum(weights)
        fused.append(ObjectState(f"fused-{index}",group[0][1].label,sum(o.x_m*w for (_,o),w in zip(group,weights))/total,sum(o.y_m*w for (_,o),w in zip(group,weights))/total,sum(o.vx_mps*w for (_,o),w in zip(group,weights))/total,sum(o.vy_mps*w for (_,o),w in zip(group,weights))/total,min(.999,1-__import__('math').prod(1-o.confidence for _,o in group)),"+".join(sorted({s for s,_ in group}))))
    return {"timestamp_ms":target,"objects":[x.to_dict() for x in fused],"rejected_sensors":sorted(set(rejected)),"source_count":len(observations)}
