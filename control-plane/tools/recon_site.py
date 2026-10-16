#!/usr/bin/env python3
"""Emit one-site documented recon; optionally summarize private local HAR safely."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import APIError
from recon_deadsimplechat import MAX_HAR_BYTES, documented_recon, summarize_har


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', choices=['deadsimplechat'])
    parser.add_argument('--har', type=Path, help='Optional private local HAR; no raw data copied or sent')
    args = parser.parse_args(argv)
    try:
        if args.har:
            with args.har.open('rb') as source:
                raw = source.read(MAX_HAR_BYTES + 1)
            if len(raw) > MAX_HAR_BYTES:
                raise APIError(413, 'HAR exceeds the local 20 MiB limit')
            result = summarize_har(json.loads(raw))
        else:
            result = documented_recon()
        print(json.dumps(result, indent=2))
        return 0
    except (APIError, OSError, ValueError, TypeError, RecursionError):
        # Do not expose raw JSON decoder errors, URLs, paths or header values.
        print('Recon input rejected; check HAR shape/limits locally. No raw details exposed.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
