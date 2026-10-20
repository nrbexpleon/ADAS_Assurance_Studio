from __future__ import annotations

import json
import os
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

from . import __version__
from .evidence import verify_evidence
from .io import campaign_from_dict
from .studio import AssuranceStudio
from .synthetic import generate_campaign

ROOT = Path(__file__).resolve().parent.parent.parent
MAX_BODY = 1_000_000
MAX_REPORTS = 200


class ReportStore:
    def __init__(self, directory: str | Path | None = None, limit: int = MAX_REPORTS):
        self.directory = Path(directory) if directory else None
        self.limit = limit
        self._reports: OrderedDict[str, dict] = OrderedDict()
        self._lock = Lock()
        if self.directory:
            self.directory.mkdir(parents=True, exist_ok=True)

    def put(self, report: dict) -> None:
        run_id = report["run_id"]
        with self._lock:
            self._reports[run_id] = report
            self._reports.move_to_end(run_id)
            while len(self._reports) > self.limit:
                self._reports.popitem(last=False)
            if self.directory:
                target = self.directory / f"{run_id}.json"
                temporary = target.with_suffix(".tmp")
                temporary.write_text(json.dumps(report, separators=(",", ":")), encoding="utf-8")
                temporary.replace(target)

    def get(self, run_id: str) -> dict | None:
        with self._lock:
            value = self._reports.get(run_id)
            if value is not None:
                return value
        if self.directory and run_id and all(c.isalnum() or c == "-" for c in run_id):
            target = self.directory / f"{run_id}.json"
            if target.is_file():
                return json.loads(target.read_text(encoding="utf-8"))
        return None


STORE = ReportStore(os.getenv("REPORT_DIR"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self.send_json(200, {"status": "ok", "version": __version__})
        if path.startswith("/api/reports/"):
            if not self.authorized():
                return self.send_json(401, {"error": "unauthorized"})
            value = STORE.get(path.rsplit("/", 1)[-1])
            return self.send_json(200, value) if value else self.send_json(404, {"error": "not-found"})
        files = {"/": "index.html", "/app.js": "app.js", "/styles.css": "styles.css"}
        if path in files:
            return self.send_file(ROOT / "public" / files[path])
        return self.send_json(404, {"error": "not-found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in {"/api/runs", "/api/verify"}:
            return self.send_json(404, {"error": "not-found"})
        if not self.authorized():
            return self.send_json(401, {"error": "unauthorized"})
        try:
            payload = self.read_json()
            if path == "/api/verify":
                return self.send_json(200, {"valid": verify_evidence(payload)})
            if "demo" in payload:
                demo = payload["demo"]
                frames, truths, detections, observations = generate_campaign(int(demo.get("frames", 20)), int(demo.get("seed", 42)))
                reviews = []
            else:
                frames, truths, detections, observations, reviews = campaign_from_dict(payload)
            report = AssuranceStudio().run(frames, truths, detections, observations, reviews)
            STORE.put(report)
            return self.send_json(201, report)
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            return self.send_json(400, {"error": str(exc)})

    def authorized(self) -> bool:
        token = os.getenv("API_TOKEN")
        return not token or self.headers.get("Authorization") == f"Bearer {token}"

    def read_json(self) -> dict:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise ValueError("Content-Length is required")
        length = int(raw_length)
        if length < 0 or length > MAX_BODY:
            raise ValueError("body-too-large")
        payload = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(payload, dict):
            raise ValueError("JSON root must be an object")
        return payload

    def send_json(self, status: int, value) -> None:
        data = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_common_headers()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path: Path) -> None:
        data = path.read_bytes()
        content_types = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
        self.send_response(200)
        self.send_header("Content-Type", content_types[path.suffix])
        self.send_common_headers()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_common_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'")

    def log_message(self, *args):
        pass


def make_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    server = make_server(host, port)
    print(f"Listening on http://{host}:{server.server_port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
