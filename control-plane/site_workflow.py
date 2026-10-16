"""Repository-backed sequential site locks. SITES.md is the single queue source.

Completion never follows a percentage alone: eight evidenced steps, fresh tests,
all site-specific acceptance gates and a checksum-verified Step 8 ZIP are required.
"""
from contextlib import contextmanager
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import os
import zipfile

from core import APIError
from platforms import PLATFORMS

START = '<!-- site-workflow:start -->'
END = '<!-- site-workflow:end -->'
ORDER = ['deadsimplechat', 'minnit', 'rumbletalk', 'chatwee', 'chatblink', 'strangermeetup', 'chatango', 'chatiw']
ROOT = Path(__file__).resolve().parent


def source_path(root=ROOT):
    source = root.parent / 'SITES.md'
    return source if source.is_file() else root / 'reports/SITE_WORKFLOW.md'


def initial_state(active='deadsimplechat'):
    order = [active] + [s for s in ORDER if s != active]
    return {'schema_version': 1, 'revision': 0, 'active_site': active, 'order': order,
            'sites': {key: {'state': 'active' if key == active else 'locked' if key in ORDER else value['phase'],
                            'completed_steps': [1] if key == 'deadsimplechat' else [],
                            'evidence': {'1': 'research/deadsimplechat-recon-2026-10-16/REPORT.md'} if key == 'deadsimplechat' else {},
                            'plan_path': None, 'approval': None}
                      for key, value in PLATFORMS.items() if key != 'simulator'}}


def render(state):
    rows = ['| Site | Lock | Delivery steps | Progress |', '| --- | --- | --- | --- |']
    for site in state['order'] + [s for s in state['sites'] if s not in state['order']]:
        item = state['sites'][site]
        progress = str(len(item['completed_steps']) / 8 * 100) + '%' if site in state['order'] else 'N/A'
        rows.append('| ' + ' | '.join([site, item['state'].upper(), str(len(item['completed_steps'])) + '/8' if site in state['order'] else '—', progress]) + ' |')
    return START + '\n' + '\n'.join(rows) + '\n\n<details><summary>Machine-readable queue (canonical)</summary>\n\n```json\n' + json.dumps(state, indent=2) + '\n```\n</details>\n' + END


class SiteWorkflow:
    def __init__(self, source=None, repo_root=None):
        self.source = Path(source) if source else source_path()
        self.repo_root = Path(repo_root) if repo_root else ROOT.parent

    def _load(self):
        try:
            text = self.source.read_text(encoding='utf-8')
            if len(text) > 131072 or text.count(START) != 1 or text.count(END) != 1:
                raise ValueError()
            block = text.split(START, 1)[1].split(END, 1)[0]
            state = json.loads(block.split('```json\n', 1)[1].split('\n```', 1)[0])
            if state.get('schema_version') != 1 or type(state.get('revision')) is not int or state['revision'] < 0:
                raise ValueError()
            if (not isinstance(state['order'], list) or len(state['order']) != len(ORDER)
                    or set(state['order']) != set(ORDER) or set(state['sites']) != set(PLATFORMS) - {'simulator'}):
                raise ValueError()
            expected_active, previous = None, 'done'
            for key in state['order']:
                item = state['sites'][key]
                status, steps = item['state'], item['completed_steps']
                if (status not in ('active', 'locked', 'done') or not isinstance(steps, list)
                        or any(type(n) is not int for n in steps) or steps != list(range(1, len(steps) + 1)) or len(steps) > 8
                        or set(item['evidence']) != {str(n) for n in steps}
                        or any(not isinstance(p, str) or not p for p in item['evidence'].values())):
                    raise ValueError()
                plan, approval = item.get('plan_path'), item.get('approval')
                if plan is not None and not isinstance(plan, str):
                    raise ValueError()
                if approval is not None and (not isinstance(approval, dict)
                        or set(approval) != {'plan_sha256', 'approved_at', 'reference'}
                        or not re.fullmatch(r'[a-f0-9]{64}', approval.get('plan_sha256', ''))
                        or not isinstance(approval.get('approved_at'), str)
                        or not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,128}', approval.get('reference', ''))):
                    raise ValueError()
                if status == 'done':
                    if previous != 'done' or len(steps) != 8:
                        raise ValueError()
                elif status == 'active':
                    if previous != 'done' or expected_active is not None:
                        raise ValueError()
                    expected_active = key
                elif previous not in ('active', 'locked'):
                    raise ValueError()
                previous = status
            if expected_active != state['active_site']:
                raise ValueError()
            for key in set(state['sites']) - set(ORDER):
                if (state['sites'][key]['state'] != PLATFORMS[key]['phase'] or state['sites'][key]['completed_steps']
                        or state['sites'][key]['evidence']):
                    raise ValueError()
            return text, state
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError):
            raise APIError(503, 'Site workflow is missing/invalid; no unlock permitted')

    @contextmanager
    def _exclusive(self):
        # Dedicated stable inode: atomic replacement of SITES cannot bypass lock.
        import fcntl  # CLI/mutations require POSIX; read-only dashboard is portable.
        lock = self.repo_root / '.runtime/site-workflow.lock'
        lock.parent.mkdir(parents=True, exist_ok=True)
        with lock.open('a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def _save(self, text, state):
        replacement = text.split(START, 1)[0] + render(state) + text.split(END, 1)[1]
        # Same-directory atomic replace; preserve all text outside the queue block.
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.source.parent, prefix='.site-workflow-', delete=False) as handle:
            handle.write(replacement)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(handle.name, self.source)

    def _evidence_path(self, value):
        if not isinstance(value, str) or len(value) > 256:
            raise APIError(400, 'Provide a repository-relative evidence path')
        path = Path(value)
        if (path.is_absolute() or '..' in path.parts or any(p.startswith('.') for p in path.parts)
                or not (value.startswith('research/') or value.startswith('control-plane/tests/')
                        or value == 'control-plane/data/test_results.json' or value.startswith('artifacts/'))
                or path.suffix.lower() not in ('.md', '.py', '.json', '.zip')):
            raise APIError(400, 'Evidence must be a non-secret report/test/receipt/release path')
        resolved = (self.repo_root / path).resolve()
        if self.repo_root.resolve() not in resolved.parents or not resolved.is_file():
            raise APIError(400, 'Evidence file does not exist within the repository')
        return resolved

    def _release(self, path):
        try:
            if path.suffix != '.zip' or path.stat().st_size > 32 * 1024 * 1024:
                raise ValueError()
            sidecar = path.with_suffix('.zip.sha256').read_text().split()
            if len(sidecar) != 2 or sidecar[1] != path.name or hashlib.sha256(path.read_bytes()).hexdigest() != sidecar[0]:
                raise ValueError()
            with zipfile.ZipFile(path) as archive:
                if (not archive.namelist() or len(archive.infolist()) > 1000
                        or sum(info.file_size for info in archive.infolist()) > 64 * 1024 * 1024
                        or archive.testzip() is not None):
                    raise ValueError()
        except (OSError, ValueError, zipfile.BadZipFile):
            raise APIError(409, 'Step 8 requires a valid ZIP with matching SHA-256 sidecar')

    def _plan_status(self, item):
        path = item.get('plan_path')
        if not path:
            return {'status': 'plan_required', 'path': None, 'sha256': None, 'approved': False}
        try:
            source = self._evidence_path(path)
            if source.suffix != '.md' or source.stat().st_size > 32768:
                raise APIError(400, 'Plan must be a Markdown document of at most 32 KiB')
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
        except (APIError, OSError):
            return {'status': 'plan_missing_or_invalid', 'path': path, 'sha256': None, 'approved': False}
        approval = item.get('approval')
        approved = bool(approval and approval['plan_sha256'] == digest)
        status = 'approved' if approved else 'changed_since_approval' if approval else 'awaiting_owner_approval'
        return {'status': status, 'path': path, 'sha256': digest, 'approved': approved}

    def read_plan(self):
        _, state = self._load()
        site = state['active_site']
        if not site:
            raise APIError(409, 'No active site')
        plan = self._plan_status(state['sites'][site])
        if not plan['sha256']:
            raise APIError(409, 'No valid scoped plan registered')
        source = self._evidence_path(plan['path'])
        raw = source.read_bytes()
        # Hash and displayed content must be from the same read.
        return {'site': site, 'revision': state['revision'], 'path': plan['path'],
                'plan_sha256': hashlib.sha256(raw).hexdigest(), 'markdown': raw.decode('utf-8')}

    def approve_plan(self, site, plan_sha256, reference, revision):
        # Only call after an explicit owner/operator action. Not an automatic
        # plan-ready transition, ownership proof, or permission to mark GREEN.
        with self._exclusive():
            text, state = self._load()
            self._guard(state, site, revision)
            item = state['sites'][site]
            plan = self._plan_status(item)
            if len(item['completed_steps']) < 2 or not plan['sha256']:
                raise APIError(409, 'Finish the scoped design and register its plan before approval')
            if plan_sha256 != plan['sha256']:
                raise APIError(409, 'Plan hash changed; read and explicitly approve the current plan')
            if not isinstance(reference, str) or not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,128}', reference):
                raise APIError(400, 'Use a non-secret approval reference, not message content or credentials')
            item['approval'] = {'plan_sha256': plan_sha256,
                                'approved_at': datetime.now(timezone.utc).isoformat(), 'reference': reference}
            state['revision'] += 1
            self._save(text, state)
        return self.snapshot()

    def _require_approved(self, item):
        if not self._plan_status(item)['approved']:
            raise APIError(409, 'Owner approval of the exact current plan is required before setup')

    def require_setup_approved(self, site):
        _, state = self._load()
        if site != state['active_site']:
            raise APIError(409, 'Site is locked; only the active site can run setup')
        self._require_approved(state['sites'][site])

    def _acceptance_blockers(self, site):
        from research import catalog
        data = catalog()
        item = next(s for s in data['sites'] if s['id'] == site)
        blockers = [g['label'] for g in item['gates'] if g['status'] != 'complete']
        if not data['local_test_receipt']['fresh_and_passed']:
            blockers.append('Fresh passing source-bound regression receipt')
        return blockers

    def snapshot(self):
        _, state = self._load()
        result = copy.deepcopy(state)
        for key, item in result['sites'].items():
            item['locked'] = item['state'] != 'active'
            item['percent'] = len(item['completed_steps']) / 8 * 100 if key in ORDER else None
            item['plan'] = self._plan_status(item) if key in ORDER else None
        active = state['active_site']
        blockers = list(self._acceptance_blockers(active)) if active else []
        if active and not result['sites'][active]['plan']['approved']:
            blockers.append('Owner approval of exact current plan before setup')
        if active and len(state['sites'][active]['completed_steps']) != 8:
            blockers.insert(0, 'Finish all eight evidenced delivery steps')
        if active and len(state['sites'][active]['completed_steps']) == 8:
            try:
                for value in state['sites'][active]['evidence'].values():
                    self._evidence_path(value)
                self._release(self._evidence_path(state['sites'][active]['evidence']['8']))
            except APIError as exc:
                blockers.append(str(exc))
        result['completion_blockers'] = blockers
        result['can_complete'] = active is not None and not blockers
        result['readiness'] = ('complete' if not active else 'green' if result['can_complete']
                               else result['sites'][active]['plan']['status'] if not result['sites'][active]['plan']['approved']
                               else 'setup_or_verification_pending')
        result['next_site'] = next((s for s in state['order'] if state['sites'][s]['state'] == 'locked'), None)
        return result

    def require_active(self, site):
        _, state = self._load()
        if site != state['active_site']:
            raise APIError(409, 'Site is locked; complete the active site before unlocking the next')

    def _guard(self, state, site, revision):
        if type(revision) is not int or revision != state['revision']:
            raise APIError(409, 'Stale workflow revision; refresh first')
        if site != state['active_site'] or site not in ORDER:
            raise APIError(409, 'Only the active site can advance; skipping is disabled')

    def complete_step(self, site, step, evidence, revision):
        with self._exclusive():
            text, state = self._load()
            self._guard(state, site, revision)
            item = state['sites'][site]
            if type(step) is not int or step != len(item['completed_steps']) + 1 or step > 8:
                raise APIError(409, 'Delivery steps must finish sequentially, without skip/replay')
            if step >= 3:
                self._require_approved(item)
            path = self._evidence_path(evidence)
            if step >= 6 and self._acceptance_blockers(site):
                raise APIError(409, 'Live acceptance and fresh regression gates remain incomplete')
            if step == 8:
                self._release(path)
            if step == 2:
                if path.suffix != '.md':
                    raise APIError(400, 'Step 2 requires a reviewable Markdown scope plan')
                item['plan_path'], item['approval'] = evidence, None
            item['completed_steps'].append(step)
            item['evidence'][str(step)] = evidence
            state['revision'] += 1
            self._save(text, state)
        return self.snapshot()

    def complete_and_next(self, site, revision):
        with self._exclusive():
            text, state = self._load()
            self._guard(state, site, revision)
            item = state['sites'][site]
            self._require_approved(item)
            if len(item['completed_steps']) != 8 or self._acceptance_blockers(site):
                raise APIError(409, 'Site is not complete; all steps and live acceptance evidence are required')
            for value in item['evidence'].values():
                self._evidence_path(value)
            self._release(self._evidence_path(item['evidence']['8']))
            item['state'] = 'done'
            index = state['order'].index(site) + 1
            next_site = state['order'][index] if index < len(state['order']) else None
            state['active_site'] = next_site
            if next_site:
                state['sites'][next_site]['state'] = 'active'
            state['revision'] += 1
            self._save(text, state)
        return self.snapshot()
