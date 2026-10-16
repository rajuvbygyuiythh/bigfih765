#!/usr/bin/env python3
"""Read all eight approved Europe tasks, or one site's core-evidence packet."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import APIError
from europe_workflow import SITE_IDS, worklist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', choices=SITE_IDS, help='Show one core-collection packet')
    parser.add_argument('--json', action='store_true', help='Print machine-readable worklist')
    args = parser.parse_args()
    try:
        data = worklist()
    except APIError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.site:
        site = next(s for s in data['sites'] if s['id'] == args.site)
        print(json.dumps(site, indent=2))
    elif args.json:
        print(json.dumps(data, indent=2))
    else:
        print('Europe browser work: 8/8 owner-approved; no per-site approval prompt.')
        print('ID                TYPE          WORK       NEXT       LIVE')
        for site in data['sites']:
            print(f"{site['id']:17} {site['mode']:13} UNLOCKED   {site['next_task']:13} NOT_READY")
        print('Next:', data['summary']['next_site'], '/ connection/event/ACK/close/Stop contract.')
        print('Policy pages reviewed:', data['summary']['policy_pages_reviewed'], '/ 8; Chaat tolerates disclosed +B bots subject to terms.')
        print('No network requests, provider adapters, messages or legacy queue changes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
