import json,os
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from . import __version__
from .studio import AssuranceStudio
from .synthetic import generate_campaign
ROOT=Path(__file__).resolve().parent.parent.parent;REPORTS={};MAX_BODY=1_000_000
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/health":return self.json(200,{"status":"ok","version":__version__})
        if path=="/api/demo":
            report=AssuranceStudio().run(*generate_campaign());REPORTS[report["run_id"]]=report;return self.json(200,report)
        if path.startswith("/api/reports/"):
            value=REPORTS.get(path.rsplit("/",1)[-1]);return self.json(200,value) if value else self.json(404,{"error":"not-found"})
        files={"/":"index.html","/app.js":"app.js","/styles.css":"styles.css"}
        if path in files:return self.file(ROOT/"public"/files[path])
        return self.json(404,{"error":"not-found"})
    def do_POST(self):
        if urlparse(self.path).path!="/api/demo":return self.json(404,{"error":"not-found"})
        if self.headers.get("Authorization")!=f"Bearer {os.getenv('API_TOKEN')}" and os.getenv("API_TOKEN"):return self.json(401,{"error":"unauthorized"})
        try:
            length=int(self.headers.get("Content-Length","0"));
            if length>MAX_BODY:raise ValueError("body-too-large")
            payload=json.loads(self.rfile.read(length) or b"{}");report=AssuranceStudio().run(*generate_campaign(int(payload.get("frames",20)),int(payload.get("seed",42))));REPORTS[report["run_id"]]=report;return self.json(201,report)
        except (ValueError,TypeError,json.JSONDecodeError) as exc:return self.json(400,{"error":str(exc)})
    def json(self,status,value):
        data=json.dumps(value,separators=(",",":")).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.common();self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
    def file(self,path):
        data=path.read_bytes();types={".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".css":"text/css; charset=utf-8"};self.send_response(200);self.send_header("Content-Type",types[path.suffix]);self.common();self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
    def common(self):self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'")
    def log_message(self,*args):pass
def main():
    port=int(os.getenv("PORT","8080"));server=ThreadingHTTPServer(("127.0.0.1",port),Handler);print(f"Listening on http://127.0.0.1:{port}");server.serve_forever()
if __name__=="__main__":main()
