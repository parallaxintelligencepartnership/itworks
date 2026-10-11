"""Executable current-fixture evidence, never a simulated model verdict."""
from pathlib import Path
import subprocess
import sys
import unittest

class PressureFixtureEvidence(unittest.TestCase):
    def test_case8_record_regenerates_from_actual_state(self):
        root=Path(__file__).resolve().parents[2]
        result=subprocess.run([sys.executable,str(root/'tests/pressure/harness/regenerate-fixture.py')],
            cwd=root,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
