"""Single authorized-room diagnostic transport. Disabled by default; no auto replies.

Only the operator-approved response to a fresh !orbit ping can be sent. Webhook
URL possession is a local shared-secret check, NOT a provider signature.
"""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
import re
import threading
import time
import uuid
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from contracts import identity, inspect_minnit
from core import APIError

REPLY = '[Orbit diagnostic bot] pong - requested test only.'
MAX_AGE = 300
ARM_TTL = 900
SEND_INTERVAL = 30  # Local safety policy, not a vendor rate limit.
ENDPOINT = r'https://[a-z0-9](?:[a-z0-9-]{0,62})\.minnit\.org/page/api'
MAX_RECORDS = 10000  # Fail closed; never evict dedup records automatically.


@dataclass(frozen=True)
class Settings:
    enabled: bool = False
    authorized_room: bool = False
    instance_id: str = ''
    api_url: str = ''
    api_key: str = field(default='', repr=False)
    webhook_secret: str = field(default='', repr=False)
    chat_id: str = ''
    chat_name: str = ''
    webhook_channel: str = ''
    send_channel: str = ''
    username: str = ''

    @classmethod
    def from_env(cls, env):
        return cls(enabled=env.get('ORBIT_MINNIT_DIAGNOSTICS') == '1',
                   authorized_room=env.get('ORBIT_MINNIT_AUTHORIZED') == '1',
                   **{name: env.get('MINNIT_' + name.upper(), '') for name in (
                       'instance_id', 'api_url', 'api_key', 'webhook_secret', 'chat_id',
                       'chat_name', 'webhook_channel', 'send_channel', 'username')})

    def blockers(self, operator_token):
        errors = []
        if not self.enabled:
            errors.append('ORBIT_MINNIT_DIAGNOSTICS must be 1')
        if not self.authorized_room:
            errors.append('ORBIT_MINNIT_AUTHORIZED must assert owner authorization and consenting test participants')
        if len(operator_token) < 32:
            errors.append('CONTROL_PLANE_TOKEN requires at least 32 characters for diagnostics')
        if not re.fullmatch(r'[a-f0-9]{32}', self.instance_id):
            errors.append('MINNIT_INSTANCE_ID must bind one saved Minnit instance')
        # Pin the documented organization endpoint. No arbitrary URLs, ports,
        # userinfo, queries, redirect targets or alternate private endpoints.
        if not re.fullmatch(ENDPOINT, self.api_url):
            errors.append('MINNIT_API_URL must be the documented HTTPS organization /page/api endpoint')
        if not self.api_key or len(self.api_key) > 512 or any(ord(c) < 33 or ord(c) > 126 for c in self.api_key):
            errors.append('MINNIT_API_KEY must be a server-side printable ASCII header value')
        if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', self.webhook_secret):
            errors.append('MINNIT_WEBHOOK_SECRET requires 32-128 URL-safe random characters')
        if self.webhook_secret and self.webhook_secret in (operator_token, self.api_key):
            errors.append('Webhook, operator and provider credentials must be separate')
        if self.api_key and self.api_key == operator_token:
            errors.append('Operator and provider credentials must be separate')
        for name in ('chat_id', 'webhook_channel'):
            try:
                identity(getattr(self, name), name)
            except APIError:
                errors.append('MINNIT_' + name.upper() + ' requires an explicit supported ID')
        for name in ('chat_name', 'send_channel', 'username'):
            value = getattr(self, name)
            if not value.strip() or len(value) > 64 or any(ord(c) < 32 for c in value):
                errors.append('MINNIT_' + name.upper() + ' requires 1-64 characters without controls')
        return errors


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class Outcome:
    status: str
    http_status: object = None


def classify(http_status, payload):
    if http_status == 200 and isinstance(payload, dict) and payload.get('success') is True:
        return Outcome('api_accepted', http_status)
    if (400 <= http_status < 500 or
            (http_status == 200 and isinstance(payload, dict) and payload.get('success') is False)):
        return Outcome('rejected', http_status)
    return Outcome('unknown', http_status)


def transmit(settings):
    """One attempt only; bounded response, no redirects/proxy inheritance/body logs."""
    if not re.fullmatch(ENDPOINT, settings.api_url):
        return Outcome('rejected')
    fields = {'action': 'sendmessage', 'chatname': settings.chat_name,
              'channel': settings.send_channel, 'username': settings.username, 'message': REPLY}
    try:
        request = Request(settings.api_url, data=urlencode(fields).encode(), method='POST',
                          headers={'Content-Type': 'application/x-www-form-urlencoded', 'X-Key': settings.api_key})
        opener = build_opener(ProxyHandler({}), NoRedirect())
        try:
            response = opener.open(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            code = response.code
            raw = response.read(4097)
            try:
                payload = json.loads(raw) if len(raw) <= 4096 else None
            except (ValueError, UnicodeError):
                payload = None
            return classify(code, payload)
    except Exception:
        # A timeout/reset might occur after the server applied the message.
        # Never expose exception text (it may contain keys, URLs or raw data).
        return Outcome('unknown')


class MinnitDiagnostics:
    def __init__(self, controller, settings=None, operator_token='', transport=transmit, clock=time.time):
        self.controller = controller
        self.settings = settings or Settings()
        self.operator_token = operator_token
        self.transport = transport
        self.clock = clock
        self.lock = threading.RLock()
        self.run_id = None
        self.armed_at = None
        with self.controller.lock, self.controller.db:
            self.controller.db.execute('''CREATE TABLE IF NOT EXISTS minnit_deliveries (
                id TEXT PRIMARY KEY, event_key TEXT UNIQUE NOT NULL,
                instance_id TEXT NOT NULL, run_id TEXT NOT NULL,
                status TEXT NOT NULL, event_at REAL NOT NULL, created_at REAL NOT NULL,
                updated_at REAL NOT NULL, attempted_at REAL, http_status INTEGER)''')
            self.controller.db.execute('CREATE INDEX IF NOT EXISTS minnit_delivery_time ON minnit_deliveries(created_at)')
            self.controller.db.execute("UPDATE minnit_deliveries SET status='unknown',updated_at=? WHERE status='submitting'", (self.clock(),))
            self.controller.db.execute("UPDATE minnit_deliveries SET status='cancelled',updated_at=? WHERE status='pending'", (self.clock(),))

    def _blockers(self):
        blockers = self.settings.blockers(self.operator_token)
        with self.controller.lock:
            self.controller._ensure_open()
            row = self.controller.db.execute('SELECT adapter FROM instances WHERE id=?', (self.settings.instance_id,)).fetchone()
            if not row or row[0] != 'minnit':
                blockers.append('MINNIT_INSTANCE_ID must reference an existing Minnit configuration')
        return blockers

    def _expire(self):
        if self.run_id and self.clock() - self.armed_at >= ARM_TTL:
            self.disarm()

    def status(self):
        with self.lock:
            self._expire()
            blockers = self._blockers()
            return {'mode': 'operator_approved_diagnostic', 'configured': not blockers,
                    'armed': bool(self.run_id) and not blockers, 'run_id': self.run_id,
                    'instance_id': self.settings.instance_id or None,
                    'expires_at': self.armed_at + ARM_TTL if self.run_id else None,
                    'blockers': blockers, 'automatic_replies': False,
                    'provider_signature_verified': False, 'live_validation': 'not_verified',
                    'webhook_auth': 'local URL shared secret; not provider identity proof',
                    'command': '!orbit ping', 'reply': REPLY,
                    'limits': {'command_age_seconds': MAX_AGE, 'arm_seconds': ARM_TTL,
                               'send_interval_seconds': SEND_INTERVAL, 'ledger_records': MAX_RECORDS}}

    def _require_armed(self):
        self._expire()
        if not self.run_id or self._blockers():
            raise APIError(409, 'Diagnostics are unconfigured, disarmed or expired')

    def arm(self):
        with self.lock:
            self._expire()
            if self._blockers():
                raise APIError(409, 'Complete server-side diagnostic configuration; inspect status blockers')
            if not self.run_id:
                self.run_id, self.armed_at = uuid.uuid4().hex, self.clock()
            return self.status()

    def disarm(self):
        with self.lock:
            self.run_id, self.armed_at = None, None
            with self.controller.lock, self.controller.db:
                self.controller._ensure_open()
                self.controller.db.execute("UPDATE minnit_deliveries SET status='cancelled',updated_at=? WHERE status='pending'", (self.clock(),))
                self.controller.db.execute("UPDATE minnit_deliveries SET status='unknown',updated_at=? WHERE status='submitting'", (self.clock(),))
            return {'armed': False, 'inflight_may_have_reached_provider': True}

    def authenticate_webhook(self, secret):
        # Authenticate before reading the request body. No operator-token bypass.
        expected = self.settings.webhook_secret
        if not expected or not hmac.compare_digest(secret.encode(), expected.encode()):
            raise APIError(401, 'Webhook secret required')
        with self.lock:
            self._require_armed()

    def receive(self, payload):
        with self.lock:
            self._require_armed()
            events = inspect_minnit(payload, self.settings.chat_id)
            now, candidates, ignored = self.clock(), [], 0
            batch = payload['data'] if payload.get('type') == 'chat_message' else []
            for raw, event in zip(batch, events):
                if event['channel_id'] != self.settings.webhook_channel or raw.get('chat_name') != self.settings.chat_name:
                    raise APIError(400, 'Unexpected diagnostic room name or channel')
                if event['kind'] != 'message' or event['text'].strip() != '!orbit ping':
                    ignored += 1
                    continue
                stamp = raw.get('timestamp')
                if (isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not math.isfinite(stamp)
                        or now - stamp > MAX_AGE or stamp > now + 30):
                    ignored += 1
                    continue
                namespace = [urlsplit(self.settings.api_url).hostname, event['room_id'], event['channel_id'], event['event_id']]
                key = hashlib.sha256(json.dumps(namespace, separators=(',', ':')).encode()).hexdigest()
                candidates.append((key, stamp))
            accepted, duplicate = 0, 0
            with self.controller.lock, self.controller.db:
                self.controller.db.execute('BEGIN IMMEDIATE')
                count = self.controller.db.execute('SELECT COUNT(*) FROM minnit_deliveries').fetchone()[0]
                for key, stamp in candidates:
                    if self.controller.db.execute('SELECT 1 FROM minnit_deliveries WHERE event_key=?', (key,)).fetchone():
                        duplicate += 1
                        continue
                    if count >= MAX_RECORDS:
                        raise APIError(503, 'Diagnostic ledger capacity reached; archive/rotation requires operator maintenance')
                    self.controller.db.execute('INSERT INTO minnit_deliveries VALUES (?,?,?,?,?,?,?,?,NULL,NULL)',
                        (uuid.uuid4().hex, key, self.settings.instance_id, self.run_id, 'pending', stamp, now, now))
                    count += 1
                    accepted += 1
            return {'accepted': accepted, 'duplicates': duplicate, 'ignored': ignored, 'messages_sent': 0}

    def deliveries(self):
        with self.lock, self.controller.lock:
            self._expire()
            self.controller._ensure_open()
            columns = ('id', 'instance_id', 'run_id', 'status', 'event_at', 'created_at', 'updated_at', 'attempted_at', 'http_status')
            rows = self.controller.db.execute('SELECT ' + ','.join(columns) + ' FROM minnit_deliveries ORDER BY created_at DESC,id DESC LIMIT 50').fetchall()
            return {'deliveries': [{**dict(zip(columns, row)), 'peer_delivery': 'unverified',
                                    'safe_to_blind_retry': False} for row in rows], 'retention': 'durable; no automatic eviction'}

    def approve(self, ident, run_id):
        with self.lock:
            self._require_armed()
            if not isinstance(run_id, str) or run_id != self.run_id:
                raise APIError(409, 'Stale diagnostic run; refresh before approval')
            now = self.clock()
            with self.controller.lock, self.controller.db:
                self.controller.db.execute('BEGIN IMMEDIATE')
                row = self.controller.db.execute('SELECT status,run_id,event_at,instance_id FROM minnit_deliveries WHERE id=?', (ident,)).fetchone()
                if not row:
                    raise APIError(404, 'Diagnostic delivery not found')
                if row[0] != 'pending' or row[1] != run_id or row[3] != self.settings.instance_id:
                    raise APIError(409, 'Delivery is no longer eligible; no retries allowed')
                if now - row[2] > MAX_AGE or row[2] > now + 30:
                    raise APIError(409, 'Diagnostic command expired; request a new ping')
                # Persistent across restart, not an in-memory token bucket.
                last = self.controller.db.execute('SELECT MAX(attempted_at) FROM minnit_deliveries').fetchone()[0]
                if last is not None and now - last < SEND_INTERVAL:
                    raise APIError(429, 'Local diagnostic cooldown; wait before approving another fresh command')
                self.controller.db.execute("UPDATE minnit_deliveries SET status='submitting',attempted_at=?,updated_at=? WHERE id=?", (now, now, ident))
            # Commit the one-shot intent BEFORE touching the network. The service
            # lock is held through dispatch entry so Stop cannot precede dispatch.
            # Transport runs under this lock: Stop waits for this attempt; timeout is per socket I/O, not a wall deadline.
            try:
                outcome = self.transport(self.settings)
                if not isinstance(outcome, Outcome) or outcome.status not in ('api_accepted', 'rejected', 'unknown'):
                    outcome = Outcome('unknown')
            except Exception:
                outcome = Outcome('unknown')
            with self.controller.lock, self.controller.db:
                self.controller.db.execute('UPDATE minnit_deliveries SET status=?,http_status=?,updated_at=? WHERE id=?',
                                           (outcome.status, outcome.http_status, self.clock(), ident))
            return {'id': ident, 'status': outcome.status, 'http_status': outcome.http_status,
                    'peer_delivery': 'unverified', 'safe_to_blind_retry': False}
