#!/usr/bin/env python3
"""Read or advance the sequential repository site queue; never unlock by override."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import APIError
from site_workflow import SiteWorkflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'complete-step', 'complete-and-next'])
    parser.add_argument('--site')
    parser.add_argument('--revision', type=int)
    parser.add_argument('--step', type=int)
    parser.add_argument('--evidence')
    args = parser.parse_args()
    queue = SiteWorkflow()
    try:
        if args.action == 'status':
            result = queue.snapshot()
        elif args.action == 'complete-step':
            result = queue.complete_step(args.site, args.step, args.evidence, args.revision)
        else:
            result = queue.complete_and_next(args.site, args.revision)
        print(json.dumps(result, indent=2))
        return 0
    except APIError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
