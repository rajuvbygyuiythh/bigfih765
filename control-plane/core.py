"""Local control-plane domain logic. No outbound network or third-party adapter."""
import collections
import re
import sqlite3
import threading
import time
import uuid


class APIError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class Controller:
    ADAPTERS = {"simulator", "minnit", "deadsimplechat"}
    MAX_INSTANCES = 100

    def __init__(self, database):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(database), check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS instances (id TEXT PRIMARY KEY, name TEXT NOT NULL, adapter TEXT NOT NULL, created REAL NOT NULL)")
        self.db.commit()
        self.runtime = {}
        self.audit = collections.deque(maxlen=200)
        self.closed = False
        for row in self.db.execute("SELECT id FROM instances"):
            self.runtime[row[0]] = self._fresh()

    @staticmethod
    def _fresh():
        return {"status": "stopped", "run_id": None, "started_at": None,
                "heartbeat_at": None, "checks_passed": 0, "duplicates": 0,
                "seen": collections.OrderedDict(), "logs": collections.deque(maxlen=100)}

    def _ensure_open(self):
        if self.closed:
            raise APIError(503, "Controller is shut down")

    def _row(self, ident):
        row = self.db.execute("SELECT id,name,adapter,created FROM instances WHERE id=?", (ident,)).fetchone()
        if not row:
            raise APIError(404, "Instance not found")
        return dict(zip(("id", "name", "adapter", "created_at"), row))

    def _log(self, ident, action, message):
        item = {"at": time.time(), "instance_id": ident, "action": action, "message": message}
        self.audit.append(item)
        if ident in self.runtime:
            self.runtime[ident]["logs"].append(item)

    def _view(self, row):
        state = self.runtime[row["id"]]
        return {**row, **{k: v for k, v in state.items() if k not in ("logs", "seen")},
                "mode": "synthetic" if row["adapter"] == "simulator" else "not_connected",
                "ready": row["adapter"] == "simulator"}

    def snapshot(self):
        with self.lock:
            self._ensure_open()
            rows = [self._row(r[0]) for r in self.db.execute("SELECT id FROM instances ORDER BY created,id")]
            instances = [self._view(r) for r in rows]
            return {"instances": instances, "audit": list(self.audit)[-30:],
                    "summary": {"configured": len(instances),
                                "running": sum(i["status"] == "running" for i in instances),
                                "checks_passed": sum(i["checks_passed"] for i in instances),
                                "duplicates": sum(i["duplicates"] for i in instances)},
                    "limits": {"configured_instances": self.MAX_INSTANCES},
                    "live_connections": 0, "acquisitions": None}

    def create(self, name, adapter):
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 64:
            raise APIError(400, "Name must be 1–64 characters")
        if any(ord(c) < 32 for c in name):
            raise APIError(400, "Name contains control characters")
        if not isinstance(adapter, str) or adapter not in self.ADAPTERS:
            raise APIError(400, "Unknown adapter")
        with self.lock:
            self._ensure_open()
            if len(self.runtime) >= self.MAX_INSTANCES:
                raise APIError(409, "Configured instance limit reached")
            ident = uuid.uuid4().hex
            self.db.execute("INSERT INTO instances VALUES (?,?,?,?)", (ident, name.strip(), adapter, time.time()))
            self.db.commit()
            self.runtime[ident] = self._fresh()
            self._log(ident, "created", "Configuration saved")
            return self._view(self._row(ident))

    def start(self, ident):
        with self.lock:
            self._ensure_open()
            row = self._row(ident)
            if row["adapter"] != "simulator":
                raise APIError(409, "Live adapter not implemented. Choose Synthetic sandbox for local testing.")
            state = self.runtime[ident]
            if state["status"] != "running":
                logs = state["logs"]
                state = self._fresh()
                state["logs"] = logs
                state.update(status="running", run_id=uuid.uuid4().hex, started_at=time.time(), heartbeat_at=time.time())
                self.runtime[ident] = state
                self._log(ident, "started", "Synthetic worker running; no external connection")
            return self._view(row)

    def stop(self, ident):
        with self.lock:
            self._ensure_open()
            row = self._row(ident)
            state = self.runtime[ident]
            if state["status"] == "running":
                state["status"] = "stopped"
                state["heartbeat_at"] = None
                self._log(ident, "stopped", "Worker stopped; new checks disabled")
            return self._view(row)

    def stop_all(self):
        with self.lock:
            self._ensure_open()
            for ident in list(self.runtime):
                self.stop(ident)
            return self.snapshot()

    def delete(self, ident):
        with self.lock:
            self._ensure_open()
            self._row(ident)
            if self.runtime[ident]["status"] == "running":
                raise APIError(409, "Stop the instance before deleting it")
            self.db.execute("DELETE FROM instances WHERE id=?", (ident,))
            self.db.commit()
            self._log(ident, "deleted", "Configuration deleted")
            del self.runtime[ident]

    def tick(self):
        with self.lock:
            self._ensure_open()
            for state in self.runtime.values():
                if state["status"] == "running":
                    state["heartbeat_at"] = time.time()

    def check(self, ident, event_id, run_id):
        if not isinstance(event_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", event_id):
            raise APIError(400, "Invalid synthetic event ID")
        with self.lock:
            self._ensure_open()
            self._row(ident)
            state = self.runtime[ident]
            if state["status"] != "running":
                raise APIError(409, "Instance is not running")
            if not isinstance(run_id, str) or run_id != state["run_id"]:
                raise APIError(409, "Stale run: refresh the instance before submitting")
            duplicate = event_id in state["seen"]
            if duplicate:
                state["duplicates"] += 1
                self._log(ident, "deduplicated", "Repeated synthetic event ignored")
            else:
                state["seen"][event_id] = True
                if len(state["seen"]) > 1000:
                    state["seen"].popitem(last=False)
                state["checks_passed"] += 1
                self._log(ident, "synthetic_check", "Synthetic event accepted locally; no message sent")
            return {"duplicate": duplicate, "result": "synthetic_only", "event_id": event_id}

    def logs(self, ident):
        with self.lock:
            self._ensure_open()
            self._row(ident)
            return list(self.runtime[ident]["logs"])

    def close(self):
        with self.lock:
            if not self.closed:
                self.stop_all()
                self.db.close()
                self.closed = True
