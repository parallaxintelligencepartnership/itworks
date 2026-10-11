import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

class ExecutedOvertimeFixture(unittest.TestCase):
    def test_exact_go_algorithm_regenerates_record(self):
        go = shutil.which('go')
        if not go:
            if os.environ.get('CI'):
                self.fail('CI requires provisioned Go; oracle execution cannot skip')
            self.skipTest('NOT RUN: Go unavailable; provision Go to qualify the fixture')
        fixture = ROOT/'tests/fixtures/overtime'
        with tempfile.TemporaryDirectory(prefix='itworks-go-') as tmp:
            result = subprocess.run([go,'run',str(fixture/'main.go')],
                input=(fixture/'inputs.json').read_bytes(), capture_output=True,
                cwd=tmp, env={**os.environ,'GOCACHE':tmp+'/cache'}, timeout=180)
            self.assertEqual(result.returncode,0,result.stderr.decode())
            self.assertEqual(result.stdout,(fixture/'expected.json').read_bytes())
