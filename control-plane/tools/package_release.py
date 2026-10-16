#!/usr/bin/env python3
"""Reproducible source/evidence backup. Explicit allowlist; no runtime secrets."""
import argparse
import hashlib
import io
from pathlib import Path
import re
import sys
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research import catalog

SOURCE_FILES = [
    '.gitignore', 'README.md', 'BUILD_REPORT.md', 'app.py', 'core.py', 'contracts.py',
    'research.py', 'platforms.py', 'workspace.py', 'minnit.py', 'package.json', 'package-lock.json',
    'static/index.html', 'static/app.js', 'static/style.css',
    'tests/test_control_plane.py', 'tests/test_contracts.py', 'tests/test_minnit.py', 'tests/ui.test.cjs',
    'data/site_catalog.json', 'data/test_results.json', 'tools/run_checks.py',
    'tools/package_release.py', 'tools/seed_workspace.py'
]
REPORTS = {
    'SUPPORTED_INTEGRATIONS.md': 'research/supported-integrations-2026-10-16/REPORT.md',
    'MULTIPLECHAT_REVIEW.md': 'research/multiplechat-review-2026-10-16/REPORT.md',
    'multiplechat-inventory.json': 'research/multiplechat-review-2026-10-16/inventory.json',
    'SITE_ONBOARDING.md': 'research/site-onboarding-2026-10-16/REPORT.md',
    'MINNIT_DIAGNOSTICS.md': 'research/minnit-diagnostics-2026-10-16/REPORT.md'
}


def payload():
    if not catalog()['local_test_receipt']['fresh_and_passed']:
        raise RuntimeError('Run tools/run_checks.py before packaging: test proof is missing/stale/failed')
    files = {name: (ROOT / name).read_bytes() for name in SOURCE_FILES}
    for name, repo_path in REPORTS.items():
        source = ROOT.parent / repo_path
        if not source.is_file():
            source = ROOT / 'reports' / name  # Rebuild from an extracted release.
        data = source.read_bytes()
        if name == 'SUPPORTED_INTEGRATIONS.md':
            data = data.decode().replace('../multiplechat-review-2026-10-16/REPORT.md', 'MULTIPLECHAT_REVIEW.md').encode()
        files['reports/' + name] = data
    files['MANIFEST.sha256'] = ''.join(
        hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
        for name, data in sorted(files.items())).encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo('orbit-control-plane/' + name, (2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    args = parser.parse_args()
    version = json.loads((ROOT / 'package.json').read_text())['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise RuntimeError('Invalid release version')
    output = Path(args.output) if args.output else ROOT.parent / 'artifacts' / ('orbit-control-plane-v' + version + '.zip')
    data = payload()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(digest + '  ' + output.name + '\n')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Archive CRC failure')
        print('PASS:', len(archive.namelist()), 'allowlisted files; CRC valid')
    print('ZIP:', output)
    print('SHA256:', digest)


if __name__ == '__main__':
    main()
