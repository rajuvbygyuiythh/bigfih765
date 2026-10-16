#!/usr/bin/env python3
"""Run actual local tests; persist a source-bound receipt for the dashboard."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research import source_fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ui', action='store_true', help='Also run npm/jsdom tests after npm ci')
    args = parser.parse_args()
    fingerprint = source_fingerprint()
    commands = [('python_suite', [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                ('js_syntax', ['node', '--check', 'static/app.js'])]
    if args.ui:
        commands.append(('dom_http_suite', ['npm', 'test']))
    results = []
    for ident, command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120)
            output = result.stdout + result.stderr
            print(output, end='')
            matches = re.findall(r'Ran (\d+) tests|PASS: (\d+) DOM', output)
            count = sum(int(a or b) for a, b in matches)
            results.append({'id': ident, 'exit_code': result.returncode, 'tests_ran': count})
        except (OSError, subprocess.TimeoutExpired):
            results.append({'id': ident, 'exit_code': 1, 'tests_ran': 0})
            print('FAIL:', ident, '(process unavailable or timed out)')
    unchanged = fingerprint == source_fingerprint()
    passed = all(r['exit_code'] == 0 for r in results) and unchanged
    receipt = {'schema_version': 1, 'finished_at': datetime.now(timezone.utc).isoformat(),
               'source_sha256': fingerprint, 'source_unchanged_during_tests': unchanged,
               'passed': passed, 'checks': results,
               'scope': 'Local regression only; no provider credentials or third-party delivery'}
    dest = ROOT / 'data/test_results.json'
    temp = dest.with_suffix('.tmp')
    temp.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    temp.replace(dest)
    print('Receipt:', 'PASS' if passed else 'FAIL', '(source-bound; live delivery remains unverified)')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
