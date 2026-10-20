from __future__ import annotations
from collections import defaultdict
from .models import Detection, GroundTruth, ObjectState

def match_objects(truth: tuple[ObjectState,...], detected: tuple[ObjectState,...], radius_m: float=2.0):
    if radius_m <= 0: raise ValueError("radius_m must be positive")
    candidates=[]
    for ti,t in enumerate(truth):
        for di,d in enumerate(detected):
            if t.label==d.label and t.distance(d)<=radius_m: candidates.append((t.distance(d),ti,di))
    matched_t,matched_d,pairs=set(),set(),[]
    for distance,ti,di in sorted(candidates):
        if ti not in matched_t and di not in matched_d: matched_t.add(ti);matched_d.add(di);pairs.append((truth[ti],detected[di],distance))
    return pairs, [x for i,x in enumerate(truth) if i not in matched_t], [x for i,x in enumerate(detected) if i not in matched_d]

def evaluate_perception(truths: list[GroundTruth], detections: list[Detection], radius_m: float=2.0) -> dict:
    truth_by={x.frame_id:x for x in truths}; tp=fp=fn=0; errors=[]; by_class=defaultdict(lambda:{"tp":0,"fp":0,"fn":0}); latencies=[]; memories=[]
    for detection in detections:
        if detection.frame_id not in truth_by: raise ValueError(f"missing truth for {detection.frame_id}")
        pairs,missed,ghosts=match_objects(truth_by[detection.frame_id].objects,detection.objects,radius_m)
        tp+=len(pairs);fn+=len(missed);fp+=len(ghosts);errors.extend(p[2] for p in pairs);latencies.append(detection.latency_ms);memories.append(detection.memory_mb)
        for t,_,_ in pairs: by_class[t.label]["tp"]+=1
        for x in missed: by_class[x.label]["fn"]+=1
        for x in ghosts: by_class[x.label]["fp"]+=1
    precision=tp/(tp+fp) if tp+fp else 0.0;recall=tp/(tp+fn) if tp+fn else 0.0
    return {"true_positives":tp,"false_positives":fp,"false_negatives":fn,"precision":precision,"recall":recall,"f1":2*precision*recall/(precision+recall) if precision+recall else 0.0,"mean_position_error_m":sum(errors)/len(errors) if errors else 0.0,"p95_latency_ms":percentile(latencies,.95),"peak_memory_mb":max(memories,default=0.0),"by_class":dict(by_class)}

def percentile(values:list[float], q:float)->float:
    if not values:return 0.0
    ordered=sorted(values);return ordered[min(len(ordered)-1,max(0,int((len(ordered)-1)*q+.999999)))]
