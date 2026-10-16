#!/usr/bin/env python3
"""Run before the server: save missing inactive site slots; no network or starts."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import Controller
from workspace import seed_inactive_configurations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=str(ROOT / 'runtime/control.db'))
    args = parser.parse_args()
    path = Path(args.db)
    path.parent.mkdir(parents=True, exist_ok=True)
    controller = Controller(path)
    try:
        print(json.dumps(seed_inactive_configurations(controller), indent=2))
    finally:
        controller.close()


if __name__ == '__main__':
    main()
