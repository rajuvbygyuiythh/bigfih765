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
    parser.add_argument('action', choices=['status', 'read-plan', 'approve-plan', 'complete-step', 'complete-and-next'])
    parser.add_argument('--site')
    parser.add_argument('--revision', type=int)
    parser.add_argument('--step', type=int)
    parser.add_argument('--evidence')
    parser.add_argument('--plan-sha256')
    parser.add_argument('--approval-reference', help='Record only after explicit owner approval; non-secret reference only')
    args = parser.parse_args()
    queue = SiteWorkflow()
    try:
        if args.action == 'status':
            result = queue.snapshot()
        elif args.action == 'read-plan':
            result = queue.read_plan()
        elif args.action == 'approve-plan':
            result = queue.approve_plan(args.site, args.plan_sha256, args.approval_reference, args.revision)
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
