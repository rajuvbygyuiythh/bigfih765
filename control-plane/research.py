"""Versioned research evidence with source-bound, local-test receipts."""
import copy
import hashlib
import json
from pathlib import Path

from core import APIError
from platforms import PLATFORMS

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
        if not isinstance(data, dict) or data.get('schema_version') != 1:
            raise ValueError('schema')
        identifiers = set()
        for site in data['sites']:
            if site['id'] not in PLATFORMS or site['id'] == 'simulator' or site['id'] in identifiers or len(site['gates']) != 12:
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
    coverage = receipt.get('covered_contracts', [])
    if not isinstance(coverage, list):
        coverage = []
    data = copy.deepcopy(data)
    for site in data['sites']:
        capability = PLATFORMS[site['id']]
        covered = proof and site['id'] in coverage and bool(capability['fixture_label'])
        applicable = capability['phase'] not in ('restricted', 'reference')
        for gate in site['gates']:
            if gate['id'] in ('parser_tests', 'failure_tests'):
                gate['status'] = 'complete' if covered else 'pending'
                gate['evidence'] = ('Passing local regression suite; receipt matches current source fingerprint'
                                    if covered else 'No current passing proof for this specific contract; unimplemented sites cannot inherit other tests')
        complete = sum(g['status'] == 'complete' for g in site['gates'])
        site['progress'] = {'completed': complete, 'total': 12, 'percent': round(complete / 12 * 100) if applicable else None, 'applicable': applicable,
                            'documentation_review_completed': sum(g['status'] == 'complete' for g in site['gates'][:6]),
                            'documentation_review_total': 6,
                            'meaning': 'Checklist completion, not automation success probability'}
        site['remaining'] = [g['label'] for g in site['gates'] if g['status'] != 'complete']
        site['can_start_live'] = False
        site['phase'] = capability['phase']
        site['configurable'] = capability['configurable']
        site['has_local_contract'] = bool(capability['fixture_label'])
        site['start_blocker'] = capability['start_blocker']
    data['summary'] = {'tracked': len(data['sites']),
                       'local_contracts': sum(s['has_local_contract'] for s in data['sites']),
                       'configurable': sum(s['configurable'] for s in data['sites']),
                       'live_connected': 0}
    data['local_test_receipt'] = {'fresh_and_passed': proof, 'finished_at': receipt.get('finished_at'),
                                'source_sha256': receipt.get('source_sha256')}
    return data
