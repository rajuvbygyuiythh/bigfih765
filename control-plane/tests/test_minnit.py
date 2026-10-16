"""Synthetic/local HTTP only. No vendor credentials, external rooms or requests."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs
from urllib.request import Request, urlopen

from app import make_server
from site_workflow import SiteWorkflow, render, initial_state
from core import APIError, Controller
from minnit import (ARM_TTL, MAX_AGE, REPLY, SEND_INTERVAL, MinnitDiagnostics,
                    NoRedirect, Outcome, Settings, classify, transmit)

TOKEN = 'operator-test-token-' + 'x' * 32
KEY = 'vendor-key-SYNTHETIC-only'
HOOK = 'webhook-test-secret-' + 'y' * 32


class Fixture(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'test.db'
        self.controller = Controller(self.path)
        self.instance = self.controller.create('Consenting test room', 'minnit')
        self.now = 1800000000.0
        self.calls = []
        self.settings = Settings(True, True, self.instance['id'], 'https://example.minnit.org/page/api',
                                 KEY, HOOK, '54', 'Main', '1', 'Main', 'OrbitTestBot')
        self.service = MinnitDiagnostics(self.controller, self.settings, TOKEN, self.transport, lambda: self.now)

    def tearDown(self):
        self.service.disarm()
        self.controller.close()
        self.directory.cleanup()

    def transport(self, config):
        self.calls.append(config)
        return Outcome('api_accepted', 200)

    def payload(self, ident='event-1', **updates):
        item = dict(msg_id=ident, chat_id='54', chat_name='Main', channel='1', user_id='synthetic-user',
                    message='!orbit ping', edited=False, timestamp=self.now,
                    ip='PRIVATE-DROP', profile_picture_url='PRIVATE-DROP', nickname='PRIVATE-DROP')
        item.update(updates)
        return {'type': 'chat_message', 'data': [item]}

    def queue(self, ident='event-1'):
        self.service.arm()
        result = self.service.receive(self.payload(ident))
        self.assertEqual(result['accepted'], 1)
        return next(x for x in self.service.deliveries()['deliveries'] if x['status'] == 'pending')

    def assert_api(self, code, function, *args):
        with self.assertRaises(APIError) as caught:
            function(*args)
        self.assertEqual(caught.exception.status, code)


class DiagnosticTests(Fixture):
    def test_default_disabled_and_strong_operator_required(self):
        disabled = MinnitDiagnostics(self.controller)
        self.assertFalse(disabled.status()['configured'])
        self.assert_api(409, disabled.arm)
        self.service.operator_token = 'short'
        self.assert_api(409, self.service.arm)
        self.assertEqual(self.calls, [])

    def test_no_secret_in_repr_status_or_ledger(self):
        self.queue()
        value = repr(self.settings) + json.dumps(self.service.status()) + json.dumps(self.service.deliveries())
        for secret in (KEY, TOKEN, HOOK, 'PRIVATE-DROP', 'synthetic-user'):
            self.assertNotIn(secret, value)
        with self.controller.lock:
            raw = '\n'.join(self.controller.db.iterdump())
        for value in (KEY, TOKEN, HOOK, 'PRIVATE-DROP', '!orbit ping', 'synthetic-user'):
            self.assertNotIn(value, raw)

    def test_config_validation_blocks_ssrf_and_incomplete_bindings(self):
        invalid = ['http://example.minnit.org/page/api', 'https://127.0.0.1/page/api',
                   'https://example.minnit.org.evil.test/page/api', 'https://example.minnit.org:443/page/api',
                   'https://user:pass@example.minnit.org/page/api', 'https://example.minnit.org/page/api?key=secret',
                   'https://example.minnit.org/page/api#fragment', 'https://example.minnit.org/other']
        for url in invalid:
            with self.subTest(url=url):
                self.assertTrue(replace(self.settings, api_url=url).blockers(TOKEN))
        for name, value in [('authorized_room', False), ('instance_id', 'invalid'), ('webhook_channel', ''),
                            ('send_channel', ''), ('chat_name', ''), ('username', ''), ('api_key', 'header\r\ninjection'),
                            ('webhook_secret', TOKEN), ('api_key', TOKEN)]:
            with self.subTest(name=name):
                self.assertTrue(replace(self.settings, **{name: value}).blockers(TOKEN))
        self.assertEqual(self.settings.blockers(TOKEN), [])
        self.service.settings = replace(self.settings, instance_id='f' * 32)
        self.assert_api(409, self.service.arm)

    def test_environment_config_is_explicit(self):
        env = {'ORBIT_MINNIT_DIAGNOSTICS': '1', 'ORBIT_MINNIT_AUTHORIZED': '1'}
        for key in ('instance_id', 'api_url', 'api_key', 'webhook_secret', 'chat_id', 'chat_name',
                    'webhook_channel', 'send_channel', 'username'):
            env['MINNIT_' + key.upper()] = getattr(self.settings, key)
        self.assertEqual(Settings.from_env(env), self.settings)
        self.assertFalse(Settings.from_env({}).enabled)

    def test_fresh_command_queued_without_network_then_approved_once(self):
        delivery = self.queue()
        self.assertEqual(self.calls, [])
        self.assertFalse(self.service.status()['automatic_replies'])
        result = self.service.approve(delivery['id'], self.service.run_id)
        self.assertEqual(result['status'], 'api_accepted')
        self.assertEqual(result['peer_delivery'], 'unverified')
        self.assertFalse(result['safe_to_blind_retry'])
        self.assertEqual(len(self.calls), 1)
        self.assert_api(409, self.service.approve, delivery['id'], self.service.run_id)
        self.assertEqual(len(self.calls), 1)

    def test_noncommand_edit_join_and_stale_commands_do_not_queue(self):
        self.service.arm()
        payloads = [self.payload(message='hello'), self.payload(edited=True),
                    self.payload(timestamp=self.now - MAX_AGE - 1), self.payload(timestamp=self.now + 31),
                    self.payload(timestamp=float('nan')), self.payload(timestamp=True), self.payload(timestamp=None),
                    {'type': 'user_joined', 'data': None}]
        for payload in payloads:
            self.assertEqual(self.service.receive(payload)['accepted'], 0)
        self.assertEqual(self.service.deliveries()['deliveries'], [])
        self.assertEqual(self.calls, [])

    def test_wrong_room_channel_name_and_partial_batch_rejected_atomically(self):
        self.service.arm()
        for changes in ({'chat_id': 'other'}, {'channel': '2'}, {'chat_name': 'Other'}):
            bad = self.payload('bad', **changes)
            bad['data'].insert(0, self.payload()['data'][0])
            self.assert_api(400, self.service.receive, bad)
            self.assertEqual(self.service.deliveries()['deliveries'], [])

    def test_persistent_duplicate_protection_after_restart(self):
        self.queue()
        self.service.disarm()
        self.controller.close()
        self.controller = Controller(self.path)
        self.service = MinnitDiagnostics(self.controller, self.settings, TOKEN, self.transport, lambda: self.now)
        self.assertFalse(self.service.status()['armed'])
        self.service.arm()
        self.assertEqual(self.service.receive(self.payload())['duplicates'], 1)
        self.assertEqual(len(self.service.deliveries()['deliveries']), 1)
        self.assertEqual(self.calls, [])

    def test_restart_marks_inflight_unknown_and_pending_cancelled(self):
        first = self.queue()
        self.service.receive(self.payload('second'))
        with self.controller.lock, self.controller.db:
            self.controller.db.execute("UPDATE minnit_deliveries SET status='submitting',attempted_at=? WHERE id=?", (self.now, first['id']))
        self.service = MinnitDiagnostics(self.controller, self.settings, TOKEN, self.transport, lambda: self.now)
        self.assertEqual({x['status'] for x in self.service.deliveries()['deliveries']}, {'unknown', 'cancelled'})
        self.service.arm()
        self.assert_api(409, self.service.approve, first['id'], self.service.run_id)
        self.assertEqual(self.calls, [])

    def test_timeout_unknown_no_blind_retry(self):
        def fail(_):
            raise TimeoutError(KEY + HOOK)
        self.service.transport = fail
        row = self.queue()
        result = self.service.approve(row['id'], self.service.run_id)
        self.assertEqual(result['status'], 'unknown')
        self.assertNotIn(KEY, json.dumps(result))
        self.assert_api(409, self.service.approve, row['id'], self.service.run_id)

    def test_cooldown_is_durable(self):
        first = self.queue()
        self.service.approve(first['id'], self.service.run_id)
        self.service.disarm()
        self.service = MinnitDiagnostics(self.controller, self.settings, TOKEN, self.transport, lambda: self.now)
        second = self.queue('second')
        self.assert_api(429, self.service.approve, second['id'], self.service.run_id)
        self.now += SEND_INTERVAL
        self.assertEqual(self.service.approve(second['id'], self.service.run_id)['status'], 'api_accepted')

    def test_arm_expiry_disarms_and_cancels(self):
        self.queue()
        self.now += ARM_TTL
        self.assertFalse(self.service.status()['armed'])
        self.assertEqual(self.service.deliveries()['deliveries'][0]['status'], 'cancelled')
        self.assert_api(409, self.service.receive, self.payload())

    def test_expired_command_and_stale_run_block_approval(self):
        row = self.queue()
        self.assert_api(409, self.service.approve, row['id'], 'old-run')
        self.now += MAX_AGE + 1
        self.assert_api(409, self.service.approve, row['id'], self.service.run_id)
        self.assertEqual(self.calls, [])

    def test_disarm_invalidates_old_work_across_rearm(self):
        row = self.queue()
        old_run = self.service.run_id
        self.service.disarm()
        self.assert_api(409, self.service.receive, self.payload('new'))
        self.service.arm()
        self.assertNotEqual(old_run, self.service.run_id)
        self.assert_api(409, self.service.approve, row['id'], self.service.run_id)
        self.assertEqual(self.calls, [])

    def test_concurrent_replays_and_approval_send_once(self):
        self.service.arm()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.service.receive(self.payload()), range(20)))
        self.assertEqual(sum(x['accepted'] for x in results), 1)
        self.assertEqual(sum(x['duplicates'] for x in results), 19)
        row = self.service.deliveries()['deliveries'][0]
        def approve(_):
            try:
                return self.service.approve(row['id'], self.service.run_id)['status']
            except APIError as exc:
                return exc.status
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(approve, range(10)))
        self.assertEqual(outcomes.count('api_accepted'), 1)
        self.assertEqual(len(self.calls), 1)

    def test_stop_waits_for_inflight_then_prevents_new_sends(self):
        started, release, stopped = threading.Event(), threading.Event(), threading.Event()
        def blocking(config):
            started.set()
            if not release.wait(3):
                raise TimeoutError()
            return self.transport(config)
        self.service.transport = blocking
        row = self.queue()
        with ThreadPoolExecutor(max_workers=2) as pool:
            send = pool.submit(self.service.approve, row['id'], self.service.run_id)
            self.assertTrue(started.wait(2))
            def stop():
                self.service.disarm()
                stopped.set()
            stop_task = pool.submit(stop)
            self.assertFalse(stopped.wait(.05))
            release.set()
            self.assertEqual(send.result(timeout=3)['status'], 'api_accepted')
            stop_task.result(timeout=3)
        self.assertTrue(stopped.is_set())
        self.assert_api(409, self.service.receive, self.payload('new'))
        self.assertEqual(len(self.calls), 1)

    def test_persist_intent_before_transport_and_capacity_fail_closed(self):
        row = self.queue()
        observations = []
        def check(_):
            other = Controller(self.path)
            try:
                persisted = other.db.execute('SELECT status,attempted_at FROM minnit_deliveries WHERE id=?', (row['id'],)).fetchone()
                observations.append(persisted)
            finally:
                other.close()
            return Outcome('unknown')
        self.service.transport = check
        self.service.approve(row['id'], self.service.run_id)
        self.assertEqual(observations, [('submitting', self.now)])
        with patch('minnit.MAX_RECORDS', 1):
            self.assert_api(503, self.service.receive, self.payload('second'))
            self.assertEqual(self.service.receive(self.payload())['duplicates'], 1)
        self.assertEqual(len(self.service.deliveries()['deliveries']), 1)


class TransportTests(unittest.TestCase):
    def test_classify_exact_ack_not_peer_delivery(self):
        for code, body, expected in [(200, {'success': True}, 'api_accepted'), (200, {'success': False}, 'rejected'),
                                     (200, {'success': 'true'}, 'unknown'), (200, None, 'unknown'),
                                     (500, {'success': True}, 'unknown'), (429, None, 'rejected'), (302, None, 'unknown')]:
            self.assertEqual(classify(code, body).status, expected)

    def test_transport_pinned_form_secret_header_fixed_reply_and_no_redirect(self):
        settings = Settings(api_url='https://example.minnit.org/page/api', api_key=KEY,
                            chat_name='Main', send_channel='Main', username='OrbitTestBot')
        response = io.BytesIO(b'{"success":true,"response":"Message sent"}')
        response.code = 200
        with patch('minnit.build_opener') as make:
            make.return_value.open.return_value = response
            self.assertEqual(transmit(settings), Outcome('api_accepted', 200))
            req = make.return_value.open.call_args.args[0]
            self.assertEqual(req.full_url, settings.api_url)
            self.assertEqual(req.get_header('X-key'), KEY)
            self.assertEqual(parse_qs(req.data.decode()), {'action': ['sendmessage'], 'chatname': ['Main'],
                              'channel': ['Main'], 'username': ['OrbitTestBot'], 'message': [REPLY]})
            self.assertEqual(make.return_value.open.call_args.kwargs['timeout'], 5)
            self.assertTrue(any(isinstance(x, NoRedirect) for x in make.call_args.args))
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.test'))

    def test_transport_refuses_unpinned_endpoint_without_opening(self):
        with patch('minnit.build_opener') as make:
            self.assertEqual(transmit(Settings(api_url='https://127.0.0.1/')).status, 'rejected')
            make.assert_not_called()

    def test_transport_bounded_body_http_errors_and_exceptions(self):
        for raw, code, expected in [(b'x' * 4097, 200, 'unknown'), (b'bad-json', 200, 'unknown'),
                                    (b'{"success":false}', 200, 'rejected')]:
            response = io.BytesIO(raw)
            response.code = code
            with patch('minnit.build_opener') as make:
                make.return_value.open.return_value = response
                self.assertEqual(transmit(Settings(api_url='https://example.minnit.org/page/api')).status, expected)
        for exception, expected in [(TimeoutError(KEY), 'unknown'),
                                    (HTTPError('https://example.minnit.org', 403, KEY, {}, io.BytesIO(b'private')), 'rejected')]:
            with patch('minnit.build_opener') as make:
                make.return_value.open.side_effect = exception
                self.assertEqual(transmit(Settings(api_url='https://example.minnit.org/page/api')).status, expected)
                self.assertEqual(make.return_value.open.call_count, 1)


class HTTPTests(Fixture):
    def setUp(self):
        super().setUp()
        workflow_source = Path(self.directory.name) / 'SITES.md'
        state = initial_state('minnit')
        plan = Path(self.directory.name) / 'research/test/PLAN.md'
        plan.parent.mkdir(parents=True)
        plan.write_text('Synthetic authorized diagnostic plan; not real owner approval')
        state['sites']['minnit'].update(completed_steps=[1,2],
            evidence={'1':'research/test/PLAN.md','2':'research/test/PLAN.md'}, plan_path='research/test/PLAN.md')
        workflow_source.write_text(render(state))
        workflow = SiteWorkflow(workflow_source, Path(self.directory.name))
        reviewed = workflow.read_plan()
        workflow.approve_plan('minnit', reviewed['plan_sha256'], 'synthetic-test-only', 0)
        self.server = make_server('127.0.0.1', 0, self.controller, TOKEN, self.service, workflow)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        super().tearDown()

    def request(self, route, data=None, token=TOKEN, extra=None, raw=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        headers.update(extra or {})
        request = Request(self.base + route, data=raw if raw is not None else json.dumps(data).encode() if data is not None else None, headers=headers)
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.code, json.load(response)

    def test_operator_auth_and_live_disabled_without_operator_token(self):
        self.assertEqual(self.request('/api/diagnostics/minnit', token='')[0], 401)
        self.assertEqual(self.request('/api/diagnostics/minnit/arm', {}, token='wrong')[0], 401)
        self.assertFalse(self.request('/api/diagnostics/minnit')[1]['armed'])
        self.assertEqual(self.request('/api/diagnostics/minnit/arm', {})[0], 200)
        with self.assertRaises(ValueError):
            make_server('127.0.0.1', 0, self.controller, '', self.service)

    def test_webhook_auth_before_body_and_browser_origin_rejected(self):
        self.service.arm()
        code, _ = self.request('/hooks/minnit/wrong', raw=b'not-json', token=TOKEN)
        self.assertEqual(code, 401)
        code, _ = self.request('/hooks/minnit/' + HOOK, self.payload(), token='', extra={'Origin': 'https://evil.test'})
        self.assertEqual(code, 403)
        code, result = self.request('/hooks/minnit/' + HOOK, self.payload(), token='')
        self.assertEqual(code, 200)
        self.assertEqual(result['messages_sent'], 0)
        self.assertEqual(self.calls, [])

    def test_full_local_pipeline_approval_no_arbitrary_message_input(self):
        self.request('/api/diagnostics/minnit/arm', {})
        self.assertEqual(self.request('/hooks/minnit/' + HOOK, self.payload(), token='')[0], 200)
        row = self.request('/api/diagnostics/minnit/deliveries')[1]['deliveries'][0]
        route = '/api/diagnostics/minnit/deliveries/' + row['id'] + '/approve'
        self.assertEqual(self.request(route, {'run_id': self.service.run_id, 'message': 'arbitrary'})[0], 400)
        self.assertEqual(self.request(route, {'run_id': self.service.run_id}, extra={'Origin': 'https://evil.test'})[0], 403)
        code, result = self.request(route, {'run_id': self.service.run_id})
        self.assertEqual((code, result['status']), (200, 'api_accepted'))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.request(route, {'run_id': self.service.run_id})[0], 409)

    def test_stop_all_and_bound_stop_cancel_pending(self):
        for route in ['/api/stop-all', '/api/instances/' + self.instance['id'] + '/stop']:
            self.service.arm()
            self.service.receive(self.payload(route.replace('/', '-')))
            self.assertEqual(self.request(route, {})[0], 200)
            self.assertFalse(self.service.status()['armed'])
            self.assertTrue(all(x['status'] == 'cancelled' for x in self.service.deliveries()['deliveries']))
        self.assertEqual(self.calls, [])

    def test_bound_delete_disarms_and_retains_ledger(self):
        self.queue()
        request = Request(self.base + '/api/instances/' + self.instance['id'], method='DELETE', data=b'{}',
                          headers={'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'})
        with urlopen(request, timeout=5) as response:
            self.assertEqual(response.code, 200)
        self.assertFalse(self.service.status()['armed'])
        self.assertFalse(self.service.status()['configured'])
        self.assertEqual(len(self.service.deliveries()['deliveries']), 1)

    def test_webhook_size_type_and_disarmed_gates(self):
        self.assertEqual(self.request('/hooks/minnit/' + HOOK, self.payload(), token='')[0], 409)
        self.service.arm()
        self.assertEqual(self.request('/hooks/minnit/' + HOOK, raw=b'{' + b'x' * 17000, token='')[0], 413)
        self.assertEqual(self.request('/hooks/minnit/' + HOOK, self.payload(), token='', extra={'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('/hooks/minnit/' + HOOK + '?key=bad', self.payload(), token='')[0], 400)


if __name__ == '__main__':
    unittest.main()
