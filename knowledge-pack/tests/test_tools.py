"""Offline regression tests for the handoff tools only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ToolsTests(unittest.TestCase):
    def run_tool(self, *args, root=ROOT):
        return subprocess.run([sys.executable, *map(str, args)], cwd=root,
                              capture_output=True, text=True)

    def test_known_method(self):
        result = self.run_tool(ROOT / 'tools/query_methods.py', '--repo',
                               'chatfilehere', '--name', 'new_conversation')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('EvaFlowBot.new_conversation', result.stdout)

    def test_go_method(self):
        result = self.run_tool(ROOT / 'tools/query_methods.py', '--repo',
                               'bigfih765', '--name', 'StartBot', '--limit', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('StartBot', result.stdout)
        self.assertIn('shown 1', result.stdout)

    def test_no_match(self):
        result = self.run_tool(ROOT / 'tools/query_methods.py', '--name',
                               'not-a-real-method-7f1b')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Found 0', result.stdout)

    def test_invalid_limit(self):
        result = self.run_tool(ROOT / 'tools/query_methods.py', '--limit', '0')
        self.assertNotEqual(result.returncode, 0)

    def test_pack_validates(self):
        result = self.run_tool(ROOT / 'tools/validate_pack.py')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)

    def test_corruption_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'pack'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            with (copy / 'GOALS.md').open('a', encoding='utf-8') as file:
                file.write('\nUnexpected alteration\n')
            result = self.run_tool(copy / 'tools/validate_pack.py', root=copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Checksum mismatch: GOALS.md', result.stdout)

    def test_source_known_failure_is_documented(self):
        data = json.loads((ROOT / 'docs/repository-inventory.json').read_text())
        issue = data['python_syntax_scan']['issues']
        self.assertEqual(len(issue), 1)
        self.assertEqual(issue[0]['line'], 252)
        self.assertEqual(issue[0]['repo'], 'chatchat2222')


if __name__ == '__main__':
    unittest.main()
