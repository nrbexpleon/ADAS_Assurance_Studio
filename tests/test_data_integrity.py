import unittest

from adas_assurance.models import Detection, Frame, GroundTruth, HumanReview, ObjectState
from adas_assurance.perception import evaluate_perception, percentile
from adas_assurance.studio import AssuranceStudio


def frame(frame_id="f", speed=10):
    return Frame(frame_id, 0, "clear", "day", "urban", 100, speed, .95, .95, .9)


class DataIntegrityTests(unittest.TestCase):
    def test_missing_detection_is_false_negative(self):
        truth = GroundTruth("f", (ObjectState("1", "car", 10, 0),))
        result = evaluate_perception([truth], [])
        self.assertEqual(1, result["false_negatives"])
        self.assertEqual(0, result["recall"])
        self.assertEqual(["f"], result["missing_detection_frames"])

    def test_duplicate_truth_frame_rejected(self):
        truth = GroundTruth("f", ())
        with self.assertRaisesRegex(ValueError, "duplicate ground-truth"):
            evaluate_perception([truth, truth], [])

    def test_unknown_detection_frame_rejected(self):
        truth = GroundTruth("f", ())
        detection = Detection("other", (), 1, 1, "v1")
        with self.assertRaisesRegex(ValueError, "no ground truth"):
            evaluate_perception([truth], [detection])

    def test_frame_truth_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "frame/truth mismatch"):
            AssuranceStudio().run([frame()], [GroundTruth("other", ())], [], [])

    def test_duplicate_object_ids_rejected(self):
        item = ObjectState("1", "car", 1, 0)
        with self.assertRaisesRegex(ValueError, "unique"):
            GroundTruth("f", (item, item))

    def test_critical_scenario_requires_approved_review(self):
        expected = ObjectState("lead", "car", 10, 0, 10, 0)
        truth = GroundTruth("f", (expected,))
        detection = Detection("f", (expected,), 10, 10, "v1")
        studio = AssuranceStudio()
        report = studio.run([frame(speed=20)], [truth], [detection], [])
        self.assertFalse(report["gates"]["critical_scenarios_reviewed"])
        self.assertEqual("investigation-required", report["decision"])

        review = HumanReview("f", "safety.engineer", "approved", "Trace reviewed")
        report = studio.run([frame(speed=20)], [truth], [detection], [], [review])
        self.assertTrue(report["gates"]["critical_scenarios_reviewed"])
        self.assertEqual(1, report["review_summary"]["approved_critical_scenarios"])

    def test_rejected_review_does_not_pass_gate(self):
        expected = ObjectState("lead", "car", 10, 0, 10, 0)
        review = HumanReview("f", "reviewer", "rejected", "Evidence incomplete")
        report = AssuranceStudio().run(
            [frame(speed=20)], [GroundTruth("f", (expected,))],
            [Detection("f", (expected,), 10, 10, "v1")], [], [review]
        )
        self.assertFalse(report["gates"]["critical_scenarios_reviewed"])

    def test_unknown_review_frame_rejected(self):
        review = HumanReview("other", "reviewer", "approved", "Checked")
        with self.assertRaisesRegex(ValueError, "unknown frames"):
            AssuranceStudio().run([frame()], [GroundTruth("f", ())], [], [], [review])

    def test_percentile_quantile_is_bounded(self):
        with self.assertRaises(ValueError):
            percentile([1], 1.1)


if __name__ == "__main__":
    unittest.main()
