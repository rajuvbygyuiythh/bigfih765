"""Europe approval is work authorization, never protocol/live-delivery proof."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from core import APIError
from europe_workflow import CONTRACT_REQUIREMENTS, DATA, SITE_IDS, worklist
from platforms import registry
from research import source_fingerprint

ROOT = Path(__file__).resolve().parents[1]


class EuropeWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(DATA.read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'manifest.json'

    def load(self, value):
        self.path.write_text(json.dumps(value))
        return worklist(self.path)

    def test_all_eight_approved_without_repeat_prompt(self):
        result = worklist()
        self.assertEqual(tuple(s['id'] for s in result['sites']), SITE_IDS)
        self.assertEqual(result['summary']['work_unlocked'], 8)
        self.assertFalse(result['approval']['repeat_approval_required'])
        for site in result['sites']:
            self.assertTrue(site['work_unlocked'])
            self.assertTrue(all(task['owner_approved'] for task in site['tasks']))
            self.assertEqual(site['next_task'], 'contract')

    def test_work_approval_never_enables_runtime_or_awards_completion(self):
        result = worklist()
        self.assertFalse(result['live_enabled'])
        self.assertEqual(result['summary']['adapters_implemented'], 0)
        for site in result['sites']:
            self.assertFalse(site['live_enabled'])
            self.assertFalse(site['adapter_implemented'])
            self.assertEqual(site['tasks'][0]['state'], 'documented')
            self.assertEqual(site['tasks'][-2]['state'], 'blocked')
            self.assertEqual(set(site['core_contract']), set(CONTRACT_REQUIREMENTS))
            self.assertTrue(all(c['state'] == 'unknown' for key, c in site['core_contract'].items()
                                if key != 'permission'))

    def test_no_network_or_legacy_mutation(self):
        legacy = ROOT.parent / 'SITES.md'
        before = legacy.read_bytes()
        platforms = registry()
        with patch('socket.socket', side_effect=AssertionError('network prohibited')):
            result = worklist()
        self.assertEqual(result['external_requests'], 0)
        self.assertEqual(result['messages_sent'], 0)
        self.assertFalse(result['legacy_delivery_queue_modified'])
        self.assertEqual(legacy.read_bytes(), before)
        self.assertEqual(registry(), platforms)

    def test_exact_geography_arithmetic_and_scope_separation(self):
        rows = {s['id']: s for s in worklist()['sites']}
        expected = {'6obcy': '90.78', 'bazoocam': '56.98', 'chatroom2000': '96.35',
                    'knuddels': '92.25', 'chaat': '85.37', 'tchatche': '78.20',
                    'deutscher_chat': '97.53', 'chat4free': '91.87'}
        for key, share in expected.items():
            self.assertEqual(rows[key]['traffic']['listed_europe_share_percent'], share)
        self.assertEqual(rows['bazoocam']['traffic']['scope'], 'desktop_web')
        self.assertEqual(rows['bazoocam']['traffic']['period'], '2026-08')
        self.assertIsNone(rows['bazoocam']['traffic']['total_visits_estimate'])
        self.assertEqual(rows['6obcy']['traffic']['scope'], 'all_devices_web')
        self.assertEqual(rows['6obcy']['traffic']['total_visits_estimate'], 824070)

    def test_community_not_mislabelled_random_next(self):
        for site in worklist()['sites']:
            self.assertEqual(site['random_next'],
                             'advertised' if site['id'] in ('6obcy', 'bazoocam') else 'not_established')
        knuddels = next(s for s in worklist()['sites'] if s['id'] == 'knuddels')
        self.assertEqual(knuddels['entry'], 'account_required')
        self.assertIn('2020', knuddels['browser_limit'])

    def test_unknown_fields_do_not_forge_capabilities_or_echo_extra_payloads(self):
        marker = 'PRIVATE-EXTRA-FIELD'
        self.data['approval']['cookie'] = marker
        self.data['sites'][0]['live_enabled'] = True
        self.data['sites'][0]['tasks'] = [{'state': 'complete'}]
        self.data['sites'][0]['credential'] = marker
        self.data['sites'][0]['traffic']['listed_europe_countries'][0]['raw'] = marker
        result = self.load(self.data)
        self.assertFalse(result['sites'][0]['live_enabled'])
        self.assertNotIn(marker, json.dumps(result))
        self.assertNotIn('complete', [t['state'] for t in result['sites'][0]['tasks']])

    def test_bad_approval_and_schema_fail_closed(self):
        mutations = [lambda d: d.update(schema_version=True),
                     lambda d: d['approval'].update(provider_permission_established=True),
                     lambda d: d['approval'].update(repeat_approval_required='false'),
                     lambda d: d['approval'].update(reference='forged'),
                     lambda d: d['approval'].update(scope='enable_all_senders')]
        for mutate in mutations:
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.subTest(data=data), self.assertRaises(APIError):
                self.load(data)

    def test_missing_duplicate_and_wrong_site_order_rejected(self):
        for rows in (self.data['sites'][:-1], self.data['sites'] + self.data['sites'][:1],
                     list(reversed(self.data['sites'])), [None] * 8):
            data = copy.deepcopy(self.data)
            data['sites'] = rows
            with self.subTest(rows=rows), self.assertRaises(APIError):
                self.load(data)

    def test_invalid_url_or_traffic_source_rejected_without_echo(self):
        for url in ('http://example.test/', 'https://secret@example.test/',
                    'https://example.test/?auth=secret', 'https://example.test/#token',
                    'https://example.test:443/', 'https://[broken'):
            data = copy.deepcopy(self.data)
            data['sites'][0]['traffic']['source'] = url
            with self.subTest(url=url), self.assertRaises(APIError) as error:
                self.load(data)
            self.assertNotIn('secret', str(error.exception))

    def test_invalid_shares_counts_and_duplicate_countries_rejected(self):
        cases = ['NaN', 'Infinity', '-1', '101', '50', 90.78, True, None]
        for value in cases:
            data = copy.deepcopy(self.data)
            data['sites'][0]['traffic']['listed_europe_countries'][0]['share_percent'] = value
            with self.subTest(value=value), self.assertRaises(APIError):
                self.load(data)
        data = copy.deepcopy(self.data)
        data['sites'][0]['traffic']['listed_europe_countries'] *= 2
        with self.assertRaises(APIError):
            self.load(data)
        for value in (True, 0, -1, '824070'):
            data = copy.deepcopy(self.data)
            data['sites'][0]['traffic']['total_visits_estimate'] = value
            with self.assertRaises(APIError):
                self.load(data)

    def test_missing_corrupt_oversized_manifest_is_generic_failure(self):
        for text in ('{', 'null', '[]', ' ' * 65537):
            self.path.write_text(text)
            with self.assertRaises(APIError):
                worklist(self.path)
        with self.assertRaises(APIError):
            worklist(Path(self.temp.name) / 'missing.json')

    def test_cli_default_json_single_site_and_unknown_site(self):
        command = [sys.executable, '-B', str(ROOT / 'tools/europe_tasks.py')]
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout.count('UNLOCKED'), 8)
        result = subprocess.run(command + ['--json'], text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)['summary']['approved_sites'], 8)
        result = subprocess.run(command + ['--site', '6obcy'], text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)['id'], '6obcy')
        result = subprocess.run(command + ['--site', '../../private'], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_assessment_manifest_is_source_fingerprinted(self):
        root = Path(self.temp.name)
        (root / 'data').mkdir()
        manifest = root / 'data/europe_assessment.json'
        manifest.write_text('{}')
        before = source_fingerprint(root)
        manifest.write_text('{"changed":true}')
        self.assertNotEqual(source_fingerprint(root), before)

    def test_policy_notes_never_block_or_reorder_engineering(self):
        result = worklist()
        rows = {site['id']: site for site in result['sites']}
        self.assertEqual(result['summary']['policy_pages_reviewed'], 3)
        self.assertEqual(result['summary']['next_site'], '6obcy')
        self.assertEqual(rows['6obcy']['policy']['status'], 'restricted_client')
        self.assertEqual(rows['bazoocam']['policy']['status'], 'noncommercial_restrictions')
        self.assertIn('+B', rows['chaat']['policy']['summary'])
        for site in result['sites']:
            self.assertEqual(site['next_task'], 'contract')
            self.assertFalse(site['policy']['blocks_engineering'])
            self.assertFalse(site['policy_review']['blocking'])
            self.assertEqual(site['engineering_blockers'], [])
            self.assertEqual(site['core_contract']['permission']['state'], 'unknown')
        self.assertFalse(result['approval']['provider_permission_established'])
        data = copy.deepcopy(self.data)
        data['sites'][0]['policy']['source'] = 'http://example.test/'
        with self.assertRaises(APIError):
            self.load(data)

    def test_every_policy_status_preserves_task_and_approval_invariants(self):
        for status in ('restricted_client', 'noncommercial_restrictions',
                       'conditional_bot_tolerance', 'not_reviewed'):
            data = copy.deepcopy(self.data)
            for site in data['sites']:
                site['policy'].update(status=status,
                    source=None if status == 'not_reviewed' else site['url'],
                    reviewed_on=None if status == 'not_reviewed' else '2026-10-16')
            result = self.load(data)
            with self.subTest(status=status):
                self.assertEqual(result['summary']['next_site'], '6obcy')
                self.assertEqual(result['summary']['next_task'], 'contract')
                self.assertFalse(result['work_policy']['repeat_owner_approval_required'])
                self.assertFalse(result['work_policy']['terms_notes_block_engineering'])
                self.assertTrue(all(s['next_task'] == 'contract' and s['work_unlocked']
                                    for s in result['sites']))
                self.assertFalse(result['live_enabled'])

    def test_manifest_cannot_override_continuation_policy_or_force_live(self):
        data = copy.deepcopy(self.data)
        data['work_policy'] = {'terms_notes_block_engineering': True,
                               'repeat_owner_approval_required': True,
                               'preserve_actual_access_and_test_gates': False}
        data['sites'][0]['next_task'] = 'wait_for_owner'
        data['sites'][0]['policy']['blocks_engineering'] = True
        data['sites'][0]['live_enabled'] = True
        result = self.load(data)
        self.assertFalse(result['work_policy']['terms_notes_block_engineering'])
        self.assertFalse(result['work_policy']['repeat_owner_approval_required'])
        self.assertTrue(result['work_policy']['preserve_actual_access_and_test_gates'])
        self.assertFalse(result['work_policy']['automatic_retries'])
        self.assertEqual(result['sites'][0]['next_task'], 'contract')
        self.assertFalse(result['sites'][0]['policy']['blocks_engineering'])
        self.assertFalse(result['sites'][0]['live_enabled'])
        result['work_policy']['terms_notes_block_engineering'] = True
        self.assertFalse(worklist()['work_policy']['terms_notes_block_engineering'])

    def test_calls_return_independent_packets(self):
        result = worklist()
        result['sites'][0]['tasks'][0]['state'] = 'forged'
        result['sites'][0]['core_contract']['send_reply']['state'] = 'proven'
        again = worklist()
        self.assertEqual(again['sites'][0]['tasks'][0]['state'], 'documented')
        self.assertEqual(again['sites'][0]['core_contract']['send_reply']['state'], 'unknown')


if __name__ == '__main__':
    unittest.main()
