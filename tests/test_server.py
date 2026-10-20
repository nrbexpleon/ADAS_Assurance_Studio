import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from adas_assurance.server import ReportStore, make_server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = Request(self.base + path, data=data, headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())

    def test_health(self):
        status, payload = self.request("/api/health")
        self.assertEqual(200, status)
        self.assertEqual("ok", payload["status"])
        self.assertEqual("0.2.0", payload["version"])

    def test_demo_run_and_report_retrieval(self):
        status, report = self.request("/api/runs", {"demo": {"frames": 5, "seed": 3}})
        self.assertEqual(201, status)
        status, stored = self.request(f"/api/reports/{report['run_id']}")
        self.assertEqual(200, status)
        self.assertEqual(report["run_id"], stored["run_id"])

    def test_invalid_campaign_returns_400(self):
        with self.assertRaises(HTTPError) as context:
            self.request("/api/runs", {"frames": []})
        self.assertEqual(400, context.exception.code)

    def test_evidence_verification_endpoint(self):
        _, report = self.request("/api/runs", {"demo": {"frames": 4}})
        status, result = self.request("/api/verify", report["evidence"])
        self.assertEqual(200, status)
        self.assertTrue(result["valid"])

    def test_report_store_is_bounded_and_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ReportStore(directory, limit=2)
            for run_id in ("one", "two", "three"):
                store.put({"run_id": run_id})
            self.assertIsNone(store._reports.get("one"))
            self.assertEqual({"run_id": "one"}, ReportStore(directory).get("one"))
            self.assertTrue((Path(directory) / "one.json").is_file())


if __name__ == "__main__":
    unittest.main()
