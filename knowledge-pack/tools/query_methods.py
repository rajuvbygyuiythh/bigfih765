#!/usr/bin/env python3
"""Search documented declarations offline; never imports historical source."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='', help='Repository name substring')
    parser.add_argument('--name', default='', help='Method/declaration substring')
    parser.add_argument('--path', default='', help='Archive member path substring')
    parser.add_argument('--limit', type=int, default=40)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    data = json.loads((ROOT / 'docs/method-index.json').read_text(encoding='utf-8'))
    total = 0
    for item in data['files']:
        if args.repo.lower() not in item['repo'].lower():
            continue
        if args.path.lower() not in item['path'].lower():
            continue
        for line, name in item['methods']:
            if args.name.lower() not in name.lower():
                continue
            total += 1
            if total <= args.limit:
                print(f"{item['repo']} | {item['archive']} | {item['path']}:{line} | {name}")
    print(f'Found {total} declaration(s); shown {min(total, args.limit)}.')
    if not total:
        print('No indexed match; parser scope or a syntax error can leave declarations missing.')


if __name__ == '__main__':
    main()
