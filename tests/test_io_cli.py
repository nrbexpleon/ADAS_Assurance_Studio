import json
import tempfile
import unittest
from pathlib import Path

from adas_assurance.cli import main
from adas_assurance.evidence import verify_evidence
from adas_assurance.io import campaign_from_dict, campaign_to_dict, load_campaign, save_campaign
from adas_assurance.studio import AssuranceStudio
from adas_assurance.synthetic import generate_campaign


class IoAndCliTests(unittest.TestCase):
    def test_campaign_round_trip(self):
        campaign = generate_campaign(5, 7)
        payload = campaign_to_dict(*campaign)
        restored = campaign_from_dict(json.loads(json.dumps(payload)))
        self.assertEqual(campaign, restored[:4])
        self.assertEqual([], restored[4])

    def test_missing_campaign_field_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing fields"):
            campaign_from_dict({"frames": []})

    def test_save_and_load_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            campaign = generate_campaign(4, 9)
            save_campaign(path, campaign)
            restored = load_campaign(path)
            self.assertEqual(campaign, restored[:4])

    def test_cli_writes_example_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            example = Path(directory) / "campaign.json"
            report_path = Path(directory) / "report.json"
            self.assertEqual(0, main(["--frames", "4", "--write-example", str(example)]))
            self.assertEqual(0, main(["--input", str(example), "--output", str(report_path)]))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(verify_evidence(report["evidence"]))

    def test_cli_verifies_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            report = AssuranceStudio().run(*generate_campaign(4, 1))
            path.write_text(json.dumps(report["evidence"]), encoding="utf-8")
            self.assertEqual(0, main(["--verify-evidence", str(path)]))
            evidence = report["evidence"]
            evidence["report"]["decision"] = "tampered"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            self.assertEqual(1, main(["--verify-evidence", str(path)]))


if __name__ == "__main__":
    unittest.main()
