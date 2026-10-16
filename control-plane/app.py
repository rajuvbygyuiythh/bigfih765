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
from platforms import registry
from minnit import MinnitDiagnostics, Settings
from site_workflow import SiteWorkflow
from reply_tester import ReplyTester
from deadsimplechat import ShadowIntake, Settings as DSSettings
from server_env import load_private_env

STATIC = Path(__file__).resolve().parent / "static"


def make_server(host, port, controller, token="", diagnostics=None, workflow=None, home="workspace", shadow=None):
    tester = ReplyTester(controller)
    shadow = shadow or ShadowIntake(controller, token=token)
    workflow = workflow or SiteWorkflow()
    diagnostics = diagnostics or MinnitDiagnostics(controller, operator_token=token)
    if shadow.token != token:
        raise ValueError("Shadow and HTTP operator authentication must match")
    if diagnostics.operator_token != token:
        raise ValueError("Diagnostic and HTTP operator authentication must match")
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
                if path.startswith('/hooks/deadsimplechat/'):
                    if method != 'POST':
                        raise APIError(405,'Shadow webhook requires POST')
                    if self.headers.get('Origin') or self.headers.get('Sec-Fetch-Site'):
                        raise APIError(403,'Shadow webhook is server-to-server only')
                    shadow.authenticate(path[len('/hooks/deadsimplechat/'):])
                    if urlparse(self.path).query:
                        raise APIError(400,'Webhook query parameters are not accepted')
                    with workflow._exclusive():
                        workflow.require_setup_approved('deadsimplechat')
                        return self.respond(200,shadow.receive(self.body()))
                if path.startswith("/hooks/minnit/"):
                    if method != "POST":
                        raise APIError(405, "Webhook requires POST")
                    if self.headers.get("Origin") or self.headers.get("Sec-Fetch-Site"):
                        raise APIError(403, "Webhook is server-to-server only")
                    workflow.require_setup_approved('minnit')
                    diagnostics.authenticate_webhook(path[len("/hooks/minnit/"):])
                    if urlparse(self.path).query:
                        raise APIError(400, "Webhook query parameters are not accepted")
                    return self.respond(200, diagnostics.receive(self.body()))
                if path == "/api/info" and method == "GET":
                    return self.respond(200, {"auth_required": bool(token), "mode": "control_plane", "fleet_mode": "synthetic", "diagnostics": "minnit_operator_approved"})
                if not path.startswith("/api/"):
                    landing = {"workspace": "workspace.html", "planning": "planning.html", "tester": "test.html", "operations": "index.html"}[home]
                    files = {"/": landing, "/plan": "planning.html",
                             "/operations": landing if home in ("planning", "workspace") else "index.html",
                             "/test": landing if home in ("planning", "workspace") else "test.html",
                             "/noto-sans-bengali.ttf": "noto-sans-bengali.ttf", "/OFL-NotoSansBengali.txt": "OFL-NotoSansBengali.txt",
                             "/workspace": "workspace.html", "/workspace.js": "workspace.js", "/workspace.css": "workspace.css",
                             "/legacy/operations": "index.html", "/legacy/test": "test.html",
                             "/planning.js": "planning.js", "/planning.css": "planning.css",
                             "/test.js": "test.js", "/test.css": "test.css", "/app.js": "app.js", "/style.css": "style.css"}
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
                if path == '/api/deadsimplechat/setup' and method == 'GET':
                    report=shadow.status()
                    try:
                        workflow.require_setup_approved('deadsimplechat')
                        report['workflow_blocked']=False
                    except APIError:
                        report['workflow_blocked']=True
                        report['blockers'].append('Active owner-approved DeadSimpleChat plan required')
                    return self.respond(200,report)
                if path == '/api/deadsimplechat/shadow/disarm' and method == 'POST':
                    return self.respond(200,shadow.disarm())
                if path in ('/api/deadsimplechat/shadow/arm','/api/deadsimplechat/shadow/register') and method == 'POST':
                    with workflow._exclusive():
                        workflow.require_setup_approved('deadsimplechat')
                        if path.endswith('/arm'):
                            return self.respond(200,shadow.arm())
                        if set(data) != {'question_id','test_user_id','run_id'}:
                            raise APIError(400,'Only question_id, test_user_id and current run_id accepted')
                        return self.respond(201,shadow.register(data.get('question_id'),data.get('test_user_id'),data.get('run_id')))
                if path == "/api/reply-test/sessions" and method == "GET":
                    return self.respond(200, tester.sessions())
                if path == "/api/reply-test/sessions" and method == "POST":
                    with workflow._exclusive():
                        workflow.require_setup_approved('deadsimplechat')
                        return self.respond(201, tester.create(data.get('script')))
                test_parts = path.strip('/').split('/')
                if len(test_parts) in (4,5) and test_parts[:3] == ['api','reply-test','sessions']:
                    ident = test_parts[3]
                    if len(test_parts) == 4 and method == 'GET':
                        return self.respond(200, tester.state(ident))
                    if len(test_parts) == 5 and method == 'POST':
                        action = test_parts[4]
                        if action in ('stop','reset'):
                            return self.respond(200, tester.action(ident, action))
                        with workflow._exclusive():
                            workflow.require_setup_approved('deadsimplechat')
                            if action == 'message':
                                return self.respond(200, tester.message(ident, data.get('run_id'), data.get('event_id'), data.get('text')))
                            if action == 'start':
                                return self.respond(200, tester.action(ident, action))
                if path == "/api/workflow" and method == "GET":
                    return self.respond(200, {**workflow.snapshot(), "operator_mutations_enabled": len(token) >= 32})
                if path == "/api/workflow/plan" and method == "GET":
                    return self.respond(200, workflow.read_plan())
                if path == "/api/workflow/approve-plan" and method == "POST":
                    if len(token) < 32:
                        raise APIError(403, "Plan approval requires a strong configured operator token")
                    if set(data) != {"site", "revision", "plan_sha256", "approval_reference"}:
                        raise APIError(400, "Exact site, revision, plan_sha256 and non-secret approval_reference required")
                    return self.respond(200, workflow.approve_plan(data.get("site"), data.get("plan_sha256"),
                                                                  data.get("approval_reference"), data.get("revision")))
                if path == "/api/workflow/complete-and-next" and method == "POST":
                    if len(token) < 32:
                        raise APIError(403, "Queue mutation requires a strong configured operator token")
                    if set(data) != {"site", "revision"}:
                        raise APIError(400, "Only site and revision are accepted; no unlock override")
                    with diagnostics.lock:
                        result = workflow.complete_and_next(data.get("site"), data.get("revision"))
                        diagnostics.disarm()
                        shadow.disarm()
                        tester.stop_all()
                    return self.respond(200, result)
                if path == "/api/diagnostics/minnit" and method == "GET":
                    status = diagnostics.status()
                    try:
                        workflow.require_setup_approved('minnit')
                        status['workflow_locked'] = False
                    except APIError:
                        status['workflow_locked'] = True
                        status['blockers'].append('Minnit is workflow-locked or its current scope lacks owner approval')
                    return self.respond(200, status)
                if path == "/api/diagnostics/minnit/deliveries" and method == "GET":
                    return self.respond(200, diagnostics.deliveries())
                if path == "/api/diagnostics/minnit/arm" and method == "POST":
                    with diagnostics.lock, workflow._exclusive():
                        workflow.require_setup_approved('minnit')
                        result = diagnostics.arm()
                    return self.respond(200, result)
                if path == "/api/diagnostics/minnit/disarm" and method == "POST":
                    return self.respond(200, diagnostics.disarm())
                diagnostic_parts = path.strip("/").split("/")
                if (len(diagnostic_parts) == 6 and diagnostic_parts[:4] == ["api", "diagnostics", "minnit", "deliveries"]
                        and diagnostic_parts[5] == "approve" and method == "POST"):
                    if set(data) != {"run_id"}:
                        raise APIError(400, "Only the current diagnostic run_id is accepted; reply text is fixed")
                    with diagnostics.lock, workflow._exclusive():
                        workflow.require_setup_approved('minnit')
                        result = diagnostics.approve(diagnostic_parts[4], data.get("run_id"))
                    return self.respond(200, result)
                if path == "/api/platforms" and method == "GET":
                    return self.respond(200, {"platforms": registry(), "live_ready": 0})
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
                    with diagnostics.lock:
                        diagnostics.disarm()
                        shadow.disarm()
                        tester.stop_all()
                        result = controller.stop_all()
                    return self.respond(200, result)
                parts = path.strip("/").split("/")
                if len(parts) in (3, 4) and parts[:2] == ["api", "instances"]:
                    ident = parts[2]
                    if len(parts) == 3 and method == "DELETE":
                        with diagnostics.lock:
                            if ident == diagnostics.settings.instance_id:
                                diagnostics.disarm()
                            if ident == shadow.settings.instance_id:
                                shadow.disarm()
                            controller.delete(ident)
                        return self.respond(200, {"deleted": True})
                    if len(parts) == 4:
                        action = parts[3]
                        if action == "logs" and method == "GET":
                            return self.respond(200, {"logs": controller.logs(ident)})
                        if action == "start" and method == "POST":
                            return self.respond(200, controller.start(ident))
                        if action == "stop" and method == "POST":
                            with diagnostics.lock:
                                if ident == diagnostics.settings.instance_id:
                                    diagnostics.disarm()
                                if ident == shadow.settings.instance_id:
                                    shadow.disarm()
                                result = controller.stop(ident)
                            return self.respond(200, result)
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
    server.diagnostics = diagnostics
    server.reply_tester = tester
    server.ds_shadow = shadow
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--home", choices=["workspace", "planning", "operations", "tester"], default="workspace", help="Default: approved operator workspace; planning is read-only, operations/tester are legacy opt-ins")
    parser.add_argument("--db", default=str(Path(__file__).parent / "runtime" / "control.db"))
    parser.add_argument('--env-file',help='Explicit owner-only server env file; never sourced or auto-loaded')
    args = parser.parse_args()
    if args.env_file:
        try:
            load_private_env(args.env_file)
        except ValueError as exc:
            parser.error(str(exc))
    database = Path(args.db)
    database.parent.mkdir(parents=True, exist_ok=True)
    controller = Controller(database)
    token = os.environ.get("CONTROL_PLANE_TOKEN", "")
    diagnostics = MinnitDiagnostics(controller, Settings.from_env(os.environ), token)
    shadow = ShadowIntake(controller, DSSettings.from_env(os.environ), token)
    server = make_server(args.host, args.port, controller, token, diagnostics, home=args.home, shadow=shadow)
    stopping = threading.Event()

    def heartbeat():
        while not stopping.wait(1):
            controller.tick()

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    print(f"Control plane listening on {args.host}:{server.server_port}; home={args.home}; provider integrations opt-in/guarded; auth={'enabled' if token else 'disabled (demo only)'}", flush=True)
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
        diagnostics.disarm()
        server.reply_tester.stop_all()
        shadow.disarm()
        server.server_close()
        controller.close()


if __name__ == "__main__":
    main()
