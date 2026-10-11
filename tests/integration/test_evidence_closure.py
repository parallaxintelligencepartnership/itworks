"""Executable evidence distinctions; not a model-adherence qualification."""
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess

class EvidenceClosure(unittest.TestCase):
    def test_live_denial_cannot_supply_missing_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'login.py').write_text('def login(password):\n    return 401 if password != "correct" else 200\n')
            def execute(code):
                return subprocess.run([sys.executable,'-B','-c',code],cwd=root,capture_output=True,text=True,timeout=10)
            live=execute('from login import login; print(login("wrong"))')
            self.assertEqual(live.stdout.strip(),'401')
            self.assertEqual(list(root.glob('test_*.py')),[], 'live evidence is not a regression file')
            (root/'test_login.py').write_text('from login import login\nassert login("wrong") == 401, "bad password must be rejected"\n')
            (root/'login.py').write_text('def login(password):\n    return 200\n')
            red=execute('import test_login')
            self.assertNotEqual(red.returncode,0); self.assertIn('AssertionError: bad password must be rejected',red.stderr)
            (root/'login.py').write_text('def login(password):\n    return 401 if password != "correct" else 200\n')
            self.assertEqual(execute('import test_login').returncode,0)
            (root/'test_login.py').write_text('import missing_fixture_dependency\n')
            broken=execute('import test_login')
            self.assertIn('ModuleNotFoundError',broken.stderr)
            self.assertNotIn('AssertionError: bad password must be rejected',broken.stderr)
