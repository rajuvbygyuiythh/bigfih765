"""Synthetic queue transitions. Acceptance is mocked only in positive unit cases."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile

from app import make_server
from core import APIError, Controller
from site_workflow import ORDER, SiteWorkflow, initial_state, render


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / 'SITES.md'
        self.source.write_text('Keep prefix\n' + render(initial_state()) + '\nKeep suffix\n')
        self.queue = SiteWorkflow(self.source, self.root)
        report = self.root / 'research/test/REPORT.md'
        report.parent.mkdir(parents=True)
        report.write_text('Synthetic consenting test evidence, not live provider validation.')
        original = self.root / 'research/deadsimplechat-recon-2026-10-16/REPORT.md'
        original.parent.mkdir(parents=True)
        original.write_text('Synthetic original step 1 evidence')
        self.evidence = 'research/test/REPORT.md'
        artifact = self.root / 'artifacts/test.zip'
        artifact.parent.mkdir()
        with zipfile.ZipFile(artifact, 'w') as archive:
            archive.writestr('README.md', 'Synthetic unit-test release')
        artifact.with_suffix('.zip.sha256').write_text(hashlib.sha256(artifact.read_bytes()).hexdigest() + '  test.zip\n')
        self.release = 'artifacts/test.zip'

    def tearDown(self):
        self.tmp.cleanup()

    def assert_api(self, code, operation, *args):
        with self.assertRaises(APIError) as caught:
            operation(*args)
        self.assertEqual(caught.exception.status, code)

    def staged(self):
        # Explicit fake acceptance; never alters the real catalog/queue.
        with patch.object(self.queue, '_acceptance_blockers', return_value=[]):
            for step in range(2, 9):
                if step == 3:
                    self.approve_fixture()
                revision = self.queue.snapshot()['revision']
                self.queue.complete_step('deadsimplechat', step, self.release if step == 8 else self.evidence, revision)

    def approve_fixture(self):
        plan = self.queue.read_plan()
        self.queue.approve_plan('deadsimplechat', plan['plan_sha256'], 'synthetic-unit-test', plan['revision'])

    def test_initial_single_active_seven_locked_and_protected_references(self):
        state = self.queue.snapshot()
        self.assertEqual(state['active_site'], 'deadsimplechat')
        self.assertEqual(state['next_site'], 'minnit')
        self.assertEqual(sum(x['state'] == 'active' for x in state['sites'].values()), 1)
        self.assertEqual(sum(x['state'] == 'locked' for x in state['sites'].values()), 7)
        self.assertEqual(state['sites']['deadsimplechat']['percent'], 12.5)
        self.assertFalse(state['can_complete'])
        for site in ('chatzy', 'chitchat', 'joingy', 'isexychat'):
            self.assertTrue(state['sites'][site]['locked'])
            self.assertIsNone(state['sites'][site]['percent'])

    def test_locked_and_unknown_sites_cannot_advance(self):
        for site in ('minnit', 'unknown', 'chatzy', 'joingy'):
            self.assert_api(409, self.queue.complete_step, site, 1, self.evidence, 0)
            self.assert_api(409, self.queue.complete_and_next, site, 0)
            self.assert_api(409, self.queue.require_active, site)
        self.queue.require_active('deadsimplechat')

    def test_no_step_skip_replay_stale_or_boolean_revision(self):
        for step in (1, 3, True, 9):
            self.assert_api(409, self.queue.complete_step, 'deadsimplechat', step, self.evidence, 0)
        for revision in (1, True, None, '0'):
            self.assert_api(409, self.queue.complete_step, 'deadsimplechat', 2, self.evidence, revision)

    def test_step_persistence_atomic_write_and_surrounding_notes(self):
        state = self.queue.complete_step('deadsimplechat', 2, self.evidence, 0)
        reloaded = SiteWorkflow(self.source, self.root).snapshot()
        self.assertEqual(reloaded['revision'], 1)
        self.assertEqual(reloaded['sites']['deadsimplechat']['percent'], 25)
        self.assertEqual(state, reloaded)
        self.assertTrue(self.source.read_text().startswith('Keep prefix'))
        self.assertTrue(self.source.read_text().endswith('Keep suffix\n'))

    def test_bad_or_private_evidence_paths_rejected(self):
        for path in ('../secret', '/etc/passwd', '.env.local', 'research/.env.local',
                     'research/private.har', 'research/missing.md', 'control-plane/runtime/private.json'):
            self.assert_api(400, self.queue.complete_step, 'deadsimplechat', 2, path, 0)

    def test_symlink_outside_repo_cannot_be_evidence(self):
        with tempfile.TemporaryDirectory() as outside:
            private = Path(outside) / 'private.md'
            private.write_text('Do not read')
            link = self.root / 'research/leak.md'
            link.symlink_to(private)
            self.assert_api(400, self.queue.complete_step, 'deadsimplechat', 2, 'research/leak.md', 0)

    def test_incomplete_cannot_mark_done_or_unlock_next(self):
        self.assert_api(409, self.queue.complete_and_next, 'deadsimplechat', 0)
        self.assertTrue(self.queue.snapshot()['sites']['minnit']['locked'])

    def test_live_gates_block_step_six_even_with_local_reports(self):
        for step in range(2, 6):
            if step == 3:
                self.approve_fixture()
            self.queue.complete_step('deadsimplechat', step, self.evidence, self.queue.snapshot()['revision'])
        self.assert_api(409, self.queue.complete_step, 'deadsimplechat', 6, self.evidence, self.queue.snapshot()['revision'])
        self.assertEqual(self.queue.snapshot()['sites']['deadsimplechat']['percent'], 62.5)

    def test_eight_steps_do_not_override_acceptance(self):
        self.staged()
        self.assertFalse(self.queue.snapshot()['can_complete'])
        self.assert_api(409, self.queue.complete_and_next, 'deadsimplechat', 8)

    def test_verified_completion_unlocks_exactly_one_and_persists(self):
        self.staged()
        with patch.object(self.queue, '_acceptance_blockers', return_value=[]):
            self.assertTrue(self.queue.snapshot()['can_complete'])
            result = self.queue.complete_and_next('deadsimplechat', 8)
        self.assertEqual(result['active_site'], 'minnit')
        self.assertEqual(result['sites']['deadsimplechat']['state'], 'done')
        self.assertEqual(result['sites']['minnit']['state'], 'active')
        self.assertEqual(sum(x['state'] == 'active' for x in result['sites'].values()), 1)
        self.assertEqual(sum(x['state'] == 'locked' for x in result['sites'].values()), 6)
        self.assertEqual(SiteWorkflow(self.source, self.root).snapshot()['active_site'], 'minnit')
        self.assert_api(409, self.queue.complete_and_next, 'deadsimplechat', 8)

    def test_bad_release_checksum_blocks_completion(self):
        self.staged()
        (self.root / self.release).with_suffix('.zip.sha256').write_text('bad  test.zip')
        with patch.object(self.queue, '_acceptance_blockers', return_value=[]):
            self.assertFalse(self.queue.snapshot()['can_complete'])
            self.assert_api(409, self.queue.complete_and_next, 'deadsimplechat', 8)

    def test_concurrent_completion_only_one_transition(self):
        self.staged()
        def complete(_):
            queue = SiteWorkflow(self.source, self.root)
            with patch.object(queue, '_acceptance_blockers', return_value=[]):
                try:
                    queue.complete_and_next('deadsimplechat', 8)
                    return 200
                except APIError as exc:
                    return exc.status
        with ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(complete, range(4)))
        self.assertEqual(statuses.count(200), 1)
        self.assertEqual(statuses.count(409), 3)
        self.assertEqual(self.queue.snapshot()['active_site'], 'minnit')

    def test_invalid_missing_queue_fails_closed(self):
        for state in ('not json', render({**initial_state(), 'active_site': 'minnit'}),
                      render({**initial_state(), 'order': ['deadsimplechat'] * 8})):
            self.source.write_text(state)
            self.assert_api(503, self.queue.snapshot)
        self.assert_api(503, SiteWorkflow(self.root / 'missing.md', self.root).snapshot)

    def test_setup_waits_for_explicit_approval_of_finished_design(self):
        self.assert_api(409, self.queue.approve_plan, 'deadsimplechat', 'a'*64, 'owner-test', 0)
        self.queue.complete_step('deadsimplechat', 2, self.evidence, 0)
        self.assertEqual(self.queue.snapshot()['readiness'], 'awaiting_owner_approval')
        self.assert_api(409, self.queue.complete_step, 'deadsimplechat', 3, self.evidence, 1)
        self.assert_api(409, self.queue.require_setup_approved, 'deadsimplechat')
        self.approve_fixture()
        self.queue.require_setup_approved('deadsimplechat')
        result = self.queue.complete_step('deadsimplechat', 3, self.evidence, 2)
        self.assertEqual(result['sites']['deadsimplechat']['completed_steps'], [1,2,3])

    def test_wrong_hash_revision_site_and_reference_cannot_approve(self):
        self.queue.complete_step('deadsimplechat', 2, self.evidence, 0)
        plan = self.queue.read_plan()
        self.assertEqual(hashlib.sha256(plan['markdown'].encode()).hexdigest(), plan['plan_sha256'])
        self.assert_api(409, self.queue.approve_plan, 'deadsimplechat', 'a'*64, 'owner-test', 1)
        self.assert_api(409, self.queue.approve_plan, 'deadsimplechat', plan['plan_sha256'], 'owner-test', 0)
        self.assert_api(409, self.queue.approve_plan, 'minnit', plan['plan_sha256'], 'owner-test', 1)
        self.assert_api(400, self.queue.approve_plan, 'deadsimplechat', plan['plan_sha256'], 'not a raw chat transcript', 1)
        self.assertIsNone(self.queue.snapshot()['sites']['deadsimplechat']['approval'])

    def test_plan_edit_requires_new_owner_approval(self):
        self.queue.complete_step('deadsimplechat', 2, self.evidence, 0)
        self.approve_fixture()
        (self.root / self.evidence).write_text('Changed scope: re-approval required')
        self.assertEqual(self.queue.snapshot()['readiness'], 'changed_since_approval')
        self.assert_api(409, self.queue.require_setup_approved, 'deadsimplechat')
        self.assert_api(409, self.queue.complete_step, 'deadsimplechat', 3, self.evidence, 2)
        self.approve_fixture()
        self.queue.require_setup_approved('deadsimplechat')

    def test_approval_does_not_mean_setup_green_or_unlock(self):
        self.queue.complete_step('deadsimplechat', 2, self.evidence, 0)
        self.approve_fixture()
        state = self.queue.snapshot()
        self.assertEqual(state['readiness'], 'setup_or_verification_pending')
        self.assertFalse(state['can_complete'])
        self.assertTrue(state['sites']['minnit']['locked'])
        self.assert_api(409, self.queue.complete_and_next, 'deadsimplechat', 2)

    def test_green_requires_approved_unchanged_plan_and_all_other_gates(self):
        self.staged()
        with patch.object(self.queue, '_acceptance_blockers', return_value=[]):
            self.assertEqual(self.queue.snapshot()['readiness'], 'green')
            (self.root / self.evidence).write_text('Plan changed after test fixture green')
            self.assertNotEqual(self.queue.snapshot()['readiness'], 'green')
            self.assert_api(409, self.queue.complete_and_next, 'deadsimplechat', 8)

    def test_http_approval_is_explicit_authenticated_hash_bound_action(self):
        self.queue.complete_step('deadsimplechat', 2, self.evidence, 0)
        controller = Controller(self.root / 'approval-test.db')
        token = 'operator-test-' + 'x'*32
        server = make_server('127.0.0.1', 0, controller, token, workflow=self.queue)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def call(path, data=None, supplied=token):
            req = Request('http://127.0.0.1:' + str(server.server_port) + path,
                          data=json.dumps(data).encode() if data is not None else None,
                          headers={'Content-Type':'application/json','Authorization':'Bearer '+supplied})
            try:
                response = urlopen(req, timeout=5)
            except HTTPError as exc:
                response = exc
            with response:
                return response.code, json.load(response)
        try:
            plan = call('/api/workflow/plan')[1]
            approval = {'site':'deadsimplechat','revision':1,'plan_sha256':plan['plan_sha256'],
                        'approval_reference':'synthetic-operator-test'}
            self.assertEqual(call('/api/workflow/approve-plan', approval, 'wrong')[0], 401)
            self.assertEqual(call('/api/workflow/approve-plan', {**approval,'override':True})[0], 400)
            self.assertIsNone(self.queue.snapshot()['sites']['deadsimplechat']['approval'])
            code, state = call('/api/workflow/approve-plan', approval)
            self.assertEqual(code, 200)
            self.assertTrue(state['sites']['deadsimplechat']['plan']['approved'])
            self.assertFalse(state['can_complete'])
            self.assertEqual(state['active_site'], 'deadsimplechat')
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2); controller.close()

    def test_all_done_has_no_active_or_next_site(self):
        state = initial_state()
        state['active_site'] = None
        for site in ORDER:
            state['sites'][site] = {'state': 'done', 'completed_steps': list(range(1, 9)),
                                    'evidence': {str(n): self.evidence for n in range(1, 9)}}
        self.source.write_text(render(state))
        result = self.queue.snapshot()
        self.assertIsNone(result['active_site'])
        self.assertIsNone(result['next_site'])
        self.assertFalse(result['can_complete'])

    def test_http_read_auth_no_override_and_locked_diagnostic(self):
        controller = Controller(self.root / 'test.db')
        token = 'operator-test-' + 'x' * 32
        server = make_server('127.0.0.1', 0, controller, token, workflow=self.queue)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def call(path, data=None, supplied=token):
            request = Request('http://127.0.0.1:' + str(server.server_port) + path,
                              data=json.dumps(data).encode() if data is not None else None,
                              headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + supplied})
            try:
                response = urlopen(request, timeout=5)
            except HTTPError as exc:
                response = exc
            with response:
                return response.code, json.load(response)
        try:
            self.assertEqual(call('/api/workflow', supplied='wrong')[0], 401)
            code, result = call('/api/workflow')
            self.assertEqual(code, 200)
            self.assertEqual(result['active_site'], 'deadsimplechat')
            self.assertEqual(call('/api/workflow/complete-and-next', {'site': 'minnit', 'revision': 0})[0], 409)
            self.assertEqual(call('/api/workflow/complete-and-next', {'site': 'deadsimplechat', 'revision': 0})[0], 409)
            self.assertEqual(call('/api/workflow/complete-and-next', {'site': 'deadsimplechat', 'revision': 0, 'override': True})[0], 400)
            self.assertEqual(call('/api/diagnostics/minnit/arm', {})[0], 409)
            self.assertTrue(call('/api/diagnostics/minnit')[1]['workflow_locked'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            controller.close()


if __name__ == '__main__':
    unittest.main()
