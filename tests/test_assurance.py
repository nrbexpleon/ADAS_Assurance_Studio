import unittest
from adas_assurance.evidence import create_evidence,verify_evidence
from adas_assurance.faults import inject_fault
from adas_assurance.fusion import fuse_observations
from adas_assurance.models import Detection,Frame,GroundTruth,ObjectState,SensorObservation
from adas_assurance.odd import evaluate_odd
from adas_assurance.perception import evaluate_perception,match_objects
from adas_assurance.scenarios import classify_scenario,time_to_collision
from adas_assurance.studio import AssuranceStudio
from adas_assurance.synthetic import generate_campaign

class AssuranceTests(unittest.TestCase):
 def test_perception(self):
  t=ObjectState("1","car",10,0);d=ObjectState("d","car",10.5,0,confidence=.9);pairs,missed,ghosts=match_objects((t,),(d,));self.assertEqual(1,len(pairs));self.assertFalse(missed);self.assertFalse(ghosts)
  m=evaluate_perception([GroundTruth("f",(t,))],[Detection("f",(d,),20,100,"v1")]);self.assertEqual(1,m["true_positives"]);self.assertEqual(1,m["precision"]);self.assertEqual(1,m["recall"]);self.assertEqual(20,m["p95_latency_ms"])
 def test_fusion_and_faults(self):
  o=ObjectState("1","car",10,0,confidence=.8);a=SensorObservation("camera",100,(o,));b=SensorObservation("radar",100,(ObjectState("2","car",11,0,confidence=.9),));r=fuse_observations([a,b]);self.assertEqual(1,len(r["objects"]));self.assertIn("camera",r["objects"][0]["source"]);self.assertEqual((),inject_fault(a,"dropout").objects);self.assertFalse(inject_fault(a,"dropout").healthy);self.assertEqual(12,inject_fault(a,"position-bias",2).objects[0].x_m);self.assertLess(inject_fault(a,"confidence-loss",.3).objects[0].confidence,o.confidence)
 def test_odd(self):
  f=Frame("f",0,"clear","day","urban",100,10,.95,.95,.9);r=evaluate_odd(f);self.assertEqual("inside",r["state"]);self.assertFalse(r["human_review_required"])
  bad=Frame("b",0,"fog","day","urban",20,10,.95,.8,.5);r=evaluate_odd(bad);self.assertEqual("outside",r["state"]);self.assertIn("visibility",r["reasons"]);self.assertTrue(r["human_review_required"])
 def test_scenarios(self):
  lead=ObjectState("1","car",15,0,5,1.2);self.assertEqual(1.5,time_to_collision(15,lead));r=classify_scenario(15,(lead,));self.assertIn("cut-in",r["events"]);self.assertEqual("high",r["risk"]);self.assertTrue(r["requires_review"])
 def test_evidence(self):
  e=create_evidence({"result":"pass"});self.assertTrue(verify_evidence(e));e["report"]["result"]="fail";self.assertFalse(verify_evidence(e))
 def test_campaign(self):
  data=generate_campaign(20,7);self.assertEqual(20,len(data[0]));report=AssuranceStudio().run(*data);self.assertTrue(report["human_approval_required"]);self.assertIn(report["decision"],{"eligible-for-human-review","investigation-required"});self.assertIn("precision",report["gates"]);self.assertTrue(verify_evidence(report["evidence"]));self.assertEqual(data,generate_campaign(20,7))
 def test_validation(self):
  with self.assertRaises(ValueError):ObjectState("","car",0,0)
  with self.assertRaises(ValueError):generate_campaign(1)
  with self.assertRaises(ValueError):inject_fault(SensorObservation("x",0,()),"unknown")
  with self.assertRaises(ValueError):AssuranceStudio().run([],[],[],[])
if __name__=="__main__":unittest.main()
