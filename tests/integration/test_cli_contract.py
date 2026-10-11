"""Real lint CLI controls; no network or model invocation."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'unit'))
from support import REPO, build_state, run, tree_snapshot


class LintCLI(unittest.TestCase):
    def test_missing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            before = tree_snapshot(directory)
            result = run(['/bin/bash', REPO / 'scripts/itworks-lint.sh', directory])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('error', result.stdout.lower())
            self.assertEqual(tree_snapshot(directory), before)

    def test_missing_required_file(self):
        with tempfile.TemporaryDirectory() as directory:
            state = build_state(directory)
            (state / 'REVIEWS.md').unlink()
            before = tree_snapshot(directory)
            result = run(['/bin/bash', REPO / 'scripts/itworks-lint.sh', directory])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(tree_snapshot(directory), before)

    def test_default_cwd_and_synthetic_legacy_controls(self):
        for version in (1, 2, 3):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                build_state(directory, version=version)
                before = tree_snapshot(directory)
                result = run(['/bin/bash', REPO / 'scripts/itworks-lint.sh'], cwd=directory)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(tree_snapshot(directory), before)
