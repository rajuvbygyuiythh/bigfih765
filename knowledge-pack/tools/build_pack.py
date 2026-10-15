#!/usr/bin/env python3
"""Regenerate checksums and make a reproducible ZIP of knowledge files only."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', '.venv', 'node_modules'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='ZIP destination outside the knowledge-pack directory')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT) or output.suffix.lower() != '.zip':
        parser.error('Use a .zip output path outside the knowledge-pack directory')
    members = sorted(p for p in ROOT.rglob('*')
                     if p.is_file() and not any(x in SKIP for x in p.relative_to(ROOT).parts)
                     and p.name != 'MANIFEST.sha256')
    for path in members:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            parser.error('Symlinks or external members are not allowed')
    manifest = ROOT / 'MANIFEST.sha256'
    manifest.write_text(''.join(
        hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.relative_to(ROOT).as_posix() + '\n'
        for path in members), encoding='utf-8')
    members.append(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w') as archive:
        for path in sorted(members):
            name = 'project-build-knowledge/' + path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP integrity check failed')
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(
        checksum + '  ' + output.name + '\n', encoding='utf-8')
    print(f'Created {output.name}: {len(members)} files, {output.stat().st_size} bytes')
    print(f'SHA-256: {checksum}')


if __name__ == '__main__':
    main()
