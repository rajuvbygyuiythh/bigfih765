"""Private local TXT conversation tester. No provider adapter or outbound network.

Each manually submitted user message consumes one reply line. Persist only reply
scripts and minimal event metadata, never user messages or uploaded filenames.
"""
import hashlib
import json
import re
import time
import uuid

from core import APIError

MAX_SCRIPT_BYTES = 8192
MAX_LINES = 200
MAX_SESSIONS = 50
MAX_EVENTS = 1000


def parse_script(text):
    if not isinstance(text, str):
        raise APIError(400, 'Upload UTF-8 plain text')
    try:
        size = len(text.encode('utf-8'))
    except UnicodeError:
        raise APIError(400, 'Invalid UTF-8 text')
    if size > MAX_SCRIPT_BYTES:
        raise APIError(413, 'TXT file limit is 8 KiB')
    text = text.removeprefix('\ufeff') if hasattr(text, 'removeprefix') else text.lstrip('\ufeff')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if any((ord(c) < 32 and c not in '\n\t') or ord(c) == 127 for c in text):
        raise APIError(400, 'TXT contains unsupported control characters')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines or len(lines) > MAX_LINES or any(len(line) > 1000 for line in lines):
        raise APIError(400, 'Use 1-200 non-empty lines, at most 1000 characters each')
    return lines


class ReplyTester:
    def __init__(self, controller, clock=time.time):
        self.controller, self.clock = controller, clock
        with controller.lock, controller.db:
            controller.db.execute('''CREATE TABLE IF NOT EXISTS reply_test_sessions (
                id TEXT PRIMARY KEY, script TEXT NOT NULL, cursor INTEGER NOT NULL,
                status TEXT NOT NULL, run_id TEXT, duplicates INTEGER NOT NULL,
                created_at REAL NOT NULL, updated_at REAL NOT NULL)''')
            controller.db.execute('''CREATE TABLE IF NOT EXISTS reply_test_events (
                session_id TEXT NOT NULL, run_id TEXT NOT NULL, event_id TEXT NOT NULL,
                reply_index INTEGER NOT NULL, input_hash TEXT NOT NULL, at REAL NOT NULL,
                PRIMARY KEY(session_id,run_id,event_id))''')
            # No automatic rearming on application restart.
            controller.db.execute("UPDATE reply_test_sessions SET status='stopped',run_id=NULL WHERE status='waiting'")

    def _row(self, ident):
        self.controller._ensure_open()
        if not isinstance(ident, str) or not re.fullmatch(r'[a-f0-9]{32}', ident):
            raise APIError(404, 'Test session not found')
        row = self.controller.db.execute('SELECT * FROM reply_test_sessions WHERE id=?', (ident,)).fetchone()
        if not row:
            raise APIError(404, 'Test session not found')
        return dict(zip(('id','script','cursor','status','run_id','duplicates','created_at','updated_at'), row))

    def _view(self, row):
        lines = json.loads(row['script'])
        events = self.controller.db.execute('SELECT run_id,event_id,reply_index,at FROM reply_test_events WHERE session_id=? ORDER BY at DESC,rowid DESC LIMIT 30', (row['id'],)).fetchall()
        return {k: row[k] for k in ('id','cursor','status','run_id','duplicates','created_at','updated_at')} | {
            'mode': 'local_self_test', 'total_lines': len(lines), 'remaining': len(lines)-row['cursor'],
            'script_preview': lines, 'provider_connected': False, 'external_messages_sent': 0,
            'peer_delivery': 'not_tested', 'events': [dict(zip(('run_id','event_id','reply_index','at'), item)) for item in events]}

    def create(self, text):
        lines = parse_script(text)
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            if self.controller.db.execute('SELECT COUNT(*) FROM reply_test_sessions').fetchone()[0] >= MAX_SESSIONS:
                raise APIError(409, 'Local test session capacity reached; reuse an existing session')
            ident, now = uuid.uuid4().hex, self.clock()
            self.controller.db.execute('INSERT INTO reply_test_sessions VALUES (?,?,0,?,NULL,0,?,?)',
                                       (ident, json.dumps(lines), 'ready', now, now))
            return self._view(self._row(ident))

    def state(self, ident):
        with self.controller.lock:
            return self._view(self._row(ident))

    def action(self, ident, action):
        with self.controller.lock, self.controller.db:
            row = self._row(ident)
            if action == 'start':
                if row['status'] == 'complete':
                    raise APIError(409, 'All lines used; reset to start a fresh local test')
                if row['status'] != 'waiting':
                    self.controller.db.execute("UPDATE reply_test_sessions SET status='waiting',run_id=?,updated_at=? WHERE id=?", (uuid.uuid4().hex, self.clock(), ident))
            elif action == 'stop':
                self.controller.db.execute("UPDATE reply_test_sessions SET status=CASE WHEN status='complete' THEN 'complete' ELSE 'stopped' END,run_id=NULL,updated_at=? WHERE id=?", (self.clock(), ident))
            elif action == 'reset':
                self.controller.db.execute("UPDATE reply_test_sessions SET cursor=0,status='ready',run_id=NULL,duplicates=0,updated_at=? WHERE id=?", (self.clock(), ident))
            else:
                raise APIError(404, 'Unknown test action')
            return self._view(self._row(ident))

    def message(self, ident, run_id, event_id, text):
        if not isinstance(text, str) or not text.strip() or len(text) > 2000:
            raise APIError(400, 'Enter a user test message of 1-2000 characters')
        if not isinstance(event_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', event_id):
            raise APIError(400, 'Invalid test event ID')
        if not isinstance(run_id, str) or not re.fullmatch(r'[a-f0-9]{32}', run_id):
            raise APIError(409, 'Start a current test run first')
        try:
            digest = hashlib.sha256(text.encode()).hexdigest()
        except UnicodeError:
            raise APIError(400, 'Invalid user message encoding')
        with self.controller.lock, self.controller.db:
            # Serializes decisions even with another SQLite connection. Only one
            # application process per DB is supported; no distributed claim.
            self.controller._ensure_open()
            self.controller.db.execute('BEGIN IMMEDIATE')
            row = self._row(ident)
            if row['run_id'] != run_id:
                raise APIError(409, 'Stale or stopped run; refresh/start before sending')
            previous = self.controller.db.execute('SELECT reply_index,input_hash FROM reply_test_events WHERE session_id=? AND run_id=? AND event_id=?', (ident,run_id,event_id)).fetchone()
            duplicate = previous is not None
            if duplicate:
                if previous[1] != digest:
                    raise APIError(409, 'Event ID reused with different input')
                index = previous[0]
                self.controller.db.execute('UPDATE reply_test_sessions SET duplicates=duplicates+1 WHERE id=?', (ident,))
            else:
                if row['status'] != 'waiting':
                    raise APIError(409, 'Local script finished or test is not running')
                count = self.controller.db.execute('SELECT COUNT(*) FROM reply_test_events WHERE session_id=?', (ident,)).fetchone()[0]
                if count >= MAX_EVENTS:
                    raise APIError(409, 'Event capacity reached for this local session')
                index, now = row['cursor'], self.clock()
                lines = json.loads(row['script'])
                self.controller.db.execute('INSERT INTO reply_test_events VALUES (?,?,?,?,?,?)', (ident,run_id,event_id,index,digest,now))
                self.controller.db.execute('UPDATE reply_test_sessions SET cursor=?,status=?,updated_at=? WHERE id=?',
                    (index+1, 'complete' if index+1 == len(lines) else 'waiting', now, ident))
            return {'reply': json.loads(row['script'])[index], 'reply_index': index, 'event_id': event_id,
                    'duplicate': duplicate, 'mode': 'local_self_test', 'external_messages_sent': 0,
                    'state': self._view(self._row(ident))}

    def stop_all(self):
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self.controller.db.execute("UPDATE reply_test_sessions SET status='stopped',run_id=NULL,updated_at=? WHERE status='waiting'", (self.clock(),))
