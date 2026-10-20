from __future__ import annotations
from .models import Frame

def evaluate_odd(frame:Frame, policy:dict|None=None)->dict:
    p={"weather":{"clear","cloudy","light-rain"},"illumination":{"day","dusk","night-lit"},"road_type":{"motorway","urban","rural"},"minimum_visibility_m":80.0,"maximum_speed_mps":36.2,"minimum_map_confidence":.85,"minimum_localization_confidence":.9,"minimum_sensor_health":.8,**(policy or {})};reasons=[]
    if frame.weather not in p["weather"]:reasons.append("weather")
    if frame.illumination not in p["illumination"]:reasons.append("illumination")
    if frame.road_type not in p["road_type"]:reasons.append("road_type")
    if frame.visibility_m<p["minimum_visibility_m"]:reasons.append("visibility")
    if frame.speed_mps>p["maximum_speed_mps"]:reasons.append("speed")
    if frame.map_confidence<p["minimum_map_confidence"]:reasons.append("map_confidence")
    if frame.localization_confidence<p["minimum_localization_confidence"]:reasons.append("localization_confidence")
    if frame.sensor_health<p["minimum_sensor_health"]:reasons.append("sensor_health")
    critical={"weather","road_type","visibility","localization_confidence","sensor_health"};state="outside" if critical.intersection(reasons) else "degraded" if reasons else "inside"
    return {"frame_id":frame.frame_id,"state":state,"reasons":reasons,"human_review_required":state!="inside","recommended_response":"request-minimum-risk-transition" if state=="outside" else "continue-with-restrictions" if state=="degraded" else "continue-monitoring"}
