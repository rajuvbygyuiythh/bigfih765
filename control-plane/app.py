#!/usr/bin/env python3
"""Python 3.9+ standard-library control-plane server."""
import argparse
import hmac
import json
import mimetypes
import os
import signal
from pathlib import Path
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from core import APIError, Controller
from contracts import FIXTURES, describe_send, inspect
from research import catalog

STATIC = Path(__file__).resolve().parent / "static"


def make_server(host, port, controller, token=""):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Never log authorization headers, request bodies or URLs.

        def respond(self, status, data, mime="application/json; charset=utf-8"):
            payload = json.dumps(data).encode() if isinstance(data, (dict, list)) else data
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(payload)

        def authorized(self):
            supplied = self.headers.get("Authorization", "")
            return not token or hmac.compare_digest(supplied.encode(), ("Bearer " + token).encode())

        def body(self):
            if self.headers.get_content_type() != "application/json":
                raise APIError(415, "Use application/json")
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                raise APIError(400, "Invalid content length")
            if length < 0 or length > 16384:
                raise APIError(413, "Request body limit is 16 KiB")
            self.connection.settimeout(5)
            try:
                value = json.loads(self.rfile.read(length))
            except (ValueError, OSError):
                raise APIError(400, "Invalid JSON body")
            if not isinstance(value, dict):
                raise APIError(400, "JSON body must be an object")
            return value

        def dispatch(self, method):
            try:
                path = urlparse(self.path).path
                if path == "/api/info" and method == "GET":
                    return self.respond(200, {"auth_required": bool(token), "mode": "synthetic_control_plane"})
                if not path.startswith("/api/"):
                    files = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
                    if method != "GET" or path not in files:
                        raise APIError(404, "Not found")
                    file = STATIC / files[path]
                    return self.respond(200, file.read_bytes(), mimetypes.guess_type(str(file))[0] or "application/octet-stream")
                if not self.authorized():
                    raise APIError(401, "Operator token required")
                if method != "GET":
                    origin = self.headers.get("Origin")
                    if self.headers.get("Sec-Fetch-Site") == "cross-site" or (origin and urlparse(origin).netloc != self.headers.get("Host")):
                        raise APIError(403, "Cross-origin mutation rejected")
                    data = self.body()
                if path == "/api/research" and method == "GET":
                    return self.respond(200, catalog())
                if path == "/api/contracts" and method == "GET":
                    return self.respond(200, {"fixtures": FIXTURES, "mode": "offline_only"})
                contract_parts = path.strip("/").split("/")
                if len(contract_parts) == 4 and contract_parts[:2] == ["api", "contracts"] and method == "POST":
                    platform, action = contract_parts[2:]
                    if action == "inspect":
                        return self.respond(200, inspect(platform, data.get("payload"), data.get("expected_room_id")))
                    if action == "describe-send":
                        return self.respond(200, describe_send(platform, data))
                if path == "/api/state" and method == "GET":
                    return self.respond(200, controller.snapshot())
                if path == "/api/instances" and method == "POST":
                    return self.respond(201, controller.create(data.get("name"), data.get("adapter")))
                if path == "/api/stop-all" and method == "POST":
                    return self.respond(200, controller.stop_all())
                parts = path.strip("/").split("/")
                if len(parts) in (3, 4) and parts[:2] == ["api", "instances"]:
                    ident = parts[2]
                    if len(parts) == 3 and method == "DELETE":
                        controller.delete(ident)
                        return self.respond(200, {"deleted": True})
                    if len(parts) == 4:
                        action = parts[3]
                        if action == "logs" and method == "GET":
                            return self.respond(200, {"logs": controller.logs(ident)})
                        if action == "start" and method == "POST":
                            return self.respond(200, controller.start(ident))
                        if action == "stop" and method == "POST":
                            return self.respond(200, controller.stop(ident))
                        if action == "check" and method == "POST":
                            return self.respond(200, controller.check(ident, data.get("event_id"), data.get("run_id")))
                raise APIError(404, "API route not found")
            except APIError as exc:
                self.respond(exc.status, {"error": str(exc)})
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception:
                self.respond(500, {"error": "Internal error; no request details exposed"})

        def do_GET(self):
            self.dispatch("GET")

        def do_POST(self):
            self.dispatch("POST")

        def do_DELETE(self):
            self.dispatch("DELETE")

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--db", default=str(Path(__file__).parent / "runtime" / "control.db"))
    args = parser.parse_args()
    database = Path(args.db)
    database.parent.mkdir(parents=True, exist_ok=True)
    controller = Controller(database)
    token = os.environ.get("CONTROL_PLANE_TOKEN", "")
    server = make_server(args.host, args.port, controller, token)
    stopping = threading.Event()

    def heartbeat():
        while not stopping.wait(1):
            controller.tick()

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    print(f"Control plane listening on {args.host}:{server.server_port}; synthetic adapters only; auth={'enabled' if token else 'disabled (demo only)'}", flush=True)
    def terminate(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stopping.set()
        thread.join(timeout=3)
        server.server_close()
        controller.close()


if __name__ == "__main__":
    main()
