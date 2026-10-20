from __future__ import annotations
import random
from .models import Detection,Frame,GroundTruth,ObjectState,SensorObservation

def generate_campaign(frame_count:int=20,seed:int=42):
    if not 2<=frame_count<=10000:raise ValueError("frame_count must be 2..10000")
    rng=random.Random(seed);frames=[];truths=[];detections=[]
    for i in range(frame_count):
        truth=(ObjectState(f"lead-{i}","car",35-i*.4,0,12,0),ObjectState(f"ped-{i}","pedestrian",22,5-i*.3,0,-1.2))
        detected=tuple(ObjectState(x.object_id,x.label,x.x_m+rng.gauss(0,.3),x.y_m+rng.gauss(0,.2),x.vx_mps,x.vy_mps,.94,"camera") for x in truth)
        if i==frame_count-1:detected=detected[:-1]
        frames.append(Frame(f"frame-{i}",i*100,"clear","day","urban",180,15,.97,.98,.96))
        truths.append(GroundTruth(f"frame-{i}",truth));detections.append(Detection(f"frame-{i}",detected,25+i*.5,320,"perception-1.0"))
    radar=SensorObservation("radar",(frame_count-1)*100,tuple(ObjectState("r1","car",truths[-1].objects[0].x_m+.2,0,12,0,.9,"radar") for _ in [0]))
    camera=SensorObservation("camera",(frame_count-1)*100,tuple(ObjectState("c1","car",truths[-1].objects[0].x_m-.2,.1,12,0,.92,"camera") for _ in [0]))
    return frames,truths,detections,[camera,radar]
