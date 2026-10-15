#!/usr/bin/env python3
"""Validate the knowledge handoff, not the historical applications."""
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate():
    errors = []
    inventory = json.loads((ROOT / 'docs/repository-inventory.json').read_text(encoding='utf-8'))
    repos = inventory['repositories']
    if len(repos) != 23 or len({r['name'] for r in repos}) != 23:
        errors.append('Expected 23 unique repository records')
    if sum(len(r['archives']) for r in repos) != 19:
        errors.append('Expected 19 archive records')
    declarations = json.loads((ROOT / 'docs/method-index.json').read_text(encoding='utf-8'))
    repo_names = {r['name'] for r in repos}
    for record in declarations['files']:
        if record['repo'] not in repo_names:
            errors.append('Unknown repository in declaration index')
        if not re.fullmatch(r'[0-9a-f]{64}', record['sha256']):
            errors.append('Invalid source SHA-256')
        if any(not isinstance(line, int) or line < 1 for line, _ in record['methods']):
            errors.append('Invalid declaration line')
    for path in ROOT.rglob('*.md'):
        if '.git' in path.relative_to(ROOT).parts:
            continue
        text = path.read_text(encoding='utf-8')
        for raw in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
            url = urlsplit(raw)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f'Broken/unsafe local link: {path.relative_to(ROOT)} -> {raw}')
    manifest = ROOT / 'MANIFEST.sha256'
    if not manifest.exists():
        errors.append('MANIFEST.sha256 missing')
    else:
        listed = set()
        for entry in manifest.read_text(encoding='utf-8').splitlines():
            try:
                expected, relative = entry.split('  ', 1)
            except ValueError:
                errors.append('Malformed manifest entry')
                continue
            target = (ROOT / relative).resolve()
            if relative in listed or not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f'Missing/unsafe/duplicate manifest member: {relative}')
                continue
            listed.add(relative)
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f'Checksum mismatch: {relative}')
        actual_files = {
            p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
            if p.is_file() and '.git' not in p.relative_to(ROOT).parts
            and '__pycache__' not in p.relative_to(ROOT).parts
            and p.name != 'MANIFEST.sha256'
        }
        if listed != actual_files:
            errors.append('Manifest membership differs from knowledge files')
    if errors:
        for error in errors:
            print('FAIL:', error)
        return 1
    print(f'PASS: {len(repos)} repositories, 19 archives, declaration index, local links and checksums.')
    print('This validates the knowledge pack only; no historical application was run.')
    return 0


if __name__ == '__main__':
    sys.exit(validate())
