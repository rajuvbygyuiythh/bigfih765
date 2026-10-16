"""Versioned research evidence with source-bound, local-test receipts."""
import copy
import hashlib
import json
from pathlib import Path

from core import APIError

ROOT = Path(__file__).resolve().parent


def source_fingerprint(root=ROOT):
    files = []
    for pattern in ('*.py', 'tests/*.py', 'tests/*.cjs', 'tools/*.py', 'static/*',
                    'package.json', 'package-lock.json', 'data/site_catalog.json'):
        files.extend(p for p in root.glob(pattern) if p.is_file())
    digest = hashlib.sha256()
    for path in sorted(set(files)):
        digest.update(str(path.relative_to(root)).encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def catalog(root=ROOT):
    try:
        data = json.loads((root / 'data/site_catalog.json').read_text(encoding='utf-8'))
        if data.get('schema_version') != 1:
            raise ValueError('schema')
        identifiers = set()
        for site in data['sites']:
            if site['id'] in identifiers or len(site['gates']) != 12:
                raise ValueError('site')
            identifiers.add(site['id'])
            if len({g['id'] for g in site['gates']}) != 12:
                raise ValueError('gates')
            if any(g['status'] not in ('complete', 'pending') for g in site['gates']):
                raise ValueError('status')
            if any(not s['url'].startswith('https://') for s in site['sources']):
                raise ValueError('source')
    except (OSError, ValueError, KeyError, TypeError):
        raise APIError(503, 'Research catalog is missing or invalid')
    try:
        receipt = json.loads((root / 'data/test_results.json').read_text(encoding='utf-8'))
        suite = next(c for c in receipt['checks'] if c['id'] == 'python_suite')
        proof = (receipt['passed'] is True and receipt['source_sha256'] == source_fingerprint(root)
                 and suite['exit_code'] == 0 and suite['tests_ran'] > 0)
    except (OSError, ValueError, KeyError, TypeError, StopIteration):
        receipt = {}
        proof = False
    data = copy.deepcopy(data)
    for site in data['sites']:
        for gate in site['gates']:
            if gate.get('requires_suite'):
                gate['status'] = 'complete' if proof else 'pending'
                gate['evidence'] = ('Passing local regression suite; receipt matches current source fingerprint'
                                    if proof else 'Missing/stale/failed local test receipt; run tools/run_checks.py')
        complete = sum(g['status'] == 'complete' for g in site['gates'])
        site['progress'] = {'completed': complete, 'total': 12, 'percent': round(complete / 12 * 100),
                            'documentation_review_completed': sum(g['status'] == 'complete' for g in site['gates'][:6]),
                            'documentation_review_total': 6,
                            'meaning': 'Checklist completion, not automation success probability'}
        site['remaining'] = [g['label'] for g in site['gates'] if g['status'] != 'complete']
        site['can_start_live'] = False
    data['local_test_receipt'] = {'fresh_and_passed': proof, 'finished_at': receipt.get('finished_at'),
                                'source_sha256': receipt.get('source_sha256')}
    return data
