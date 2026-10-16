"""Single-room SHADOW intake for approved diagnostic intents. NO sender exists.

URL secret proves possession only; provider authenticity and live routing remain
unverified. Repeated button clicks consume one registered intent, not one reply
per occurrence. Do not attach the local TXT engine to this callback.
"""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import re
import time
import uuid

from core import APIError
from contracts import identity, inspect_deadsimplechat

ACTION = 'orbit_diagnostic_ping_v1'
PLAN_WINDOW = 900
INTENT_TTL = 300
MAX_INTENTS = 5000


@dataclass(frozen=True)
class Settings:
    enabled: bool = False
    authorized: bool = False
    instance_id: str = ''
    room_id: str = ''
    bot_id: str = ''
    webhook_secret: str = field(default='', repr=False)
    api_key: str = field(default='', repr=False)

    @classmethod
    def from_env(cls, env):
        return cls(env.get('DS_SHADOW_ENABLED') == '1', env.get('DS_AUTHORIZED_ROOM') == '1',
                   *(env.get('DS_' + key, '') for key in ('INSTANCE_ID','ROOM_ID','BOT_ID','WEBHOOK_SECRET','API_KEY')))


class ShadowIntake:
    def __init__(self, controller, settings=None, token='', clock=time.time):
        self.controller, self.settings, self.token, self.clock = controller, settings or Settings(), token, clock
        self.run_id, self.armed_at = None, None
        with controller.lock, controller.db:
            controller.db.execute('''CREATE TABLE IF NOT EXISTS ds_shadow_intents (
                id TEXT PRIMARY KEY, binding_hash TEXT UNIQUE NOT NULL, run_id TEXT NOT NULL,
                status TEXT NOT NULL, created_at REAL NOT NULL, expires_at REAL NOT NULL,
                matched_at REAL, duplicates INTEGER NOT NULL DEFAULT 0)''')
            controller.db.execute("UPDATE ds_shadow_intents SET status='cancelled' WHERE status='registered'")

    def _blockers(self):
        cfg, blockers = self.settings, []
        if not cfg.enabled: blockers.append('DS_SHADOW_ENABLED must be 1 for shadow-only intake')
        if not cfg.authorized: blockers.append('DS_AUTHORIZED_ROOM must assert an owned/authorized consenting test room')
        if not re.fullmatch(r'[!-~]{32,512}', self.token): blockers.append('CONTROL_PLANE_TOKEN requires 32-512 non-space printable ASCII characters')
        if not re.fullmatch(r'[a-f0-9]{32}', cfg.instance_id): blockers.append('DS_INSTANCE_ID must bind one saved DeadSimpleChat configuration')
        row = self.controller.db.execute('SELECT adapter FROM instances WHERE id=?',(cfg.instance_id,)).fetchone()
        if not row or row[0] != 'deadsimplechat': blockers.append('DS_INSTANCE_ID does not match an existing DeadSimpleChat slot')
        for key in ('room_id','bot_id'):
            try: identity(getattr(cfg,key),key)
            except APIError: blockers.append('DS_'+key.upper()+' requires an explicit supported ID')
        if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}',cfg.webhook_secret): blockers.append('DS_WEBHOOK_SECRET needs 32-128 random URL-safe characters')
        if cfg.webhook_secret and cfg.webhook_secret in (self.token,cfg.api_key): blockers.append('Operator, webhook and API credentials must be independent')
        if cfg.api_key and (cfg.api_key == self.token or not re.fullmatch(r'[!-~]{1,512}',cfg.api_key)):
            blockers.append('DS_API_KEY must be an independent printable secret without controls')
        return blockers

    def _expire(self):
        now = self.clock()
        if self.run_id and now-self.armed_at >= PLAN_WINDOW:
            self._disarm()
        self.controller.db.execute("UPDATE ds_shadow_intents SET status='expired' WHERE status='registered' AND expires_at<=?",(now,))

    def _disarm(self):
        self.run_id, self.armed_at = None, None
        self.controller.db.execute("UPDATE ds_shadow_intents SET status='cancelled' WHERE status='registered'")

    def _armed(self):
        self._expire()
        if not self.run_id or self._blockers():
            raise APIError(409,'Shadow intake is unconfigured, disarmed or expired; no live sending is available')

    def status(self):
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self._expire()
            blockers = self._blockers()
            rows = self.controller.db.execute('SELECT id,status,created_at,expires_at,matched_at,duplicates FROM ds_shadow_intents ORDER BY created_at DESC,rowid DESC LIMIT 30').fetchall()
            counts = dict(self.controller.db.execute('SELECT status,COUNT(*) FROM ds_shadow_intents GROUP BY status'))
            return {'mode':'shadow_intake_no_send','configured':not blockers,'armed':bool(self.run_id) and not blockers,
                    'run_id':self.run_id,'expires_at':self.armed_at+PLAN_WINDOW if self.run_id else None,
                    'blockers':blockers,'api_key_present':bool(self.settings.api_key),
                    'live_blockers':(['DS_API_KEY is not configured'] if not self.settings.api_key else []) + [
                        'Provider auth/header requirement unresolved; sender not implemented',
                        'URL secret is local possession only; provider callback authenticity unverified',
                        'Provider egress/callback routing/entitlement and consenting peer delivery not verified'],
                    'provider_connected':False,'vendor_signature_verified':False,'outbound_enabled':False,
                    'external_messages_sent':0,'peer_delivery':'not_tested','counts':counts,
                    'intents':[dict(zip(('id','status','created_at','expires_at','matched_at','duplicates'),r)) for r in rows]}

    def arm(self):
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self._expire()
            if self._blockers(): raise APIError(409,'Complete sanitized setup blockers before arming shadow intake')
            if not self.run_id: self.run_id,self.armed_at=uuid.uuid4().hex,self.clock()
        return self.status()

    def disarm(self):
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self._disarm()
        return {'armed':False,'external_messages_sent':0}

    def authenticate(self, secret):
        expected=self.settings.webhook_secret
        if not expected or not hmac.compare_digest(secret.encode(),expected.encode()):
            raise APIError(401,'Independent shadow webhook secret required')
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self._armed()

    def _binding(self, question, user):
        value=[self.settings.bot_id,self.settings.room_id,identity(question,'question ID'),identity(user,'test user ID'),ACTION]
        return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()

    def register(self, question, user, run_id):
        key=self._binding(question,user)
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self._armed()
            if run_id != self.run_id: raise APIError(409,'Stale shadow run')
            self.controller.db.commit()
            self.controller.db.execute('BEGIN IMMEDIATE')
            if self.controller.db.execute('SELECT 1 FROM ds_shadow_intents WHERE binding_hash=?',(key,)).fetchone():
                raise APIError(409,'Question/user/action already registered; use a fresh owned test question')
            if self.controller.db.execute('SELECT COUNT(*) FROM ds_shadow_intents').fetchone()[0] >= MAX_INTENTS:
                raise APIError(503,'Shadow ledger capacity reached; no automatic replay-key eviction')
            ident,now=uuid.uuid4().hex,self.clock()
            self.controller.db.execute('INSERT INTO ds_shadow_intents VALUES (?,?,?,?,?,?,NULL,0)',
                (ident,key,self.run_id,'registered',now,min(now+INTENT_TTL,self.armed_at+PLAN_WINDOW)))
            return {'id':ident,'status':'registered','external_messages_sent':0}

    def receive(self, payload):
        # Full shape/scope validation precedes any persistent change.
        event=inspect_deadsimplechat(payload,self.settings.room_id)[0]
        bot=payload.get('bot');message=payload.get('message');action=payload['actionButtonPressed']
        if (not isinstance(bot,dict) or identity(bot.get('_id'),'bot ID') != self.settings.bot_id
                or not isinstance(message,dict) or identity(message.get('_id'),'question ID') != event['parent_message_id']
                or event['action_id'] != ACTION or action.get('type') != 'action'):
            raise APIError(400,'Unexpected bot, parent question or action binding')
        key=self._binding(event['parent_message_id'],event['sender_id'])
        with self.controller.lock, self.controller.db:
            self.controller._ensure_open()
            self._armed()
            # _armed may update expirations, beginning a transaction. Commit that
            # before starting the serialized compare/update transaction below.
            self.controller.db.commit()
            self.controller.db.execute('BEGIN IMMEDIATE')
            row=self.controller.db.execute('SELECT id,status,run_id FROM ds_shadow_intents WHERE binding_hash=?',(key,)).fetchone()
            if not row or row[2] != self.run_id or row[1] not in ('registered','matched'):
                return {'status':'shadow_ignored','matched':False,'external_messages_sent':0}
            duplicate=row[1]=='matched'
            if duplicate: self.controller.db.execute('UPDATE ds_shadow_intents SET duplicates=duplicates+1 WHERE id=?',(row[0],))
            else: self.controller.db.execute("UPDATE ds_shadow_intents SET status='matched',matched_at=? WHERE id=?",(self.clock(),row[0]))
            return {'id':row[0],'status':'shadow_matched_no_send','matched':True,'duplicate':duplicate,
                    'provider_identity_verified':False,'external_messages_sent':0}
