"""Prove developer test subprocesses do not execute caller Git hooks."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import REPO


class TestIsolation(unittest.TestCase):
    def test_inherited_git_hooks_cannot_run_in_fixture_tests(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);hooks=root/'hooks';hooks.mkdir();sentinel=root/'hook-ran'
            hook=hooks/'pre-commit'
            hook.write_text('#!/bin/bash\ntouch "$ITWORKS_HOOK_SENTINEL"\n');hook.chmod(0o700)
            config=root/'config';config.write_text('[core]\n hooksPath = '+str(hooks)+'\n')
            env=os.environ.copy()
            for key in list(env):
                if key.startswith('GIT_CONFIG_'):env.pop(key)
            env.update(GIT_CONFIG_GLOBAL=str(config),GIT_CONFIG_NOSYSTEM='1',ITWORKS_HOOK_SENTINEL=str(sentinel),PYTHONPATH=str(REPO/'tests/integration')+os.pathsep+str(REPO/'tests/unit'))
            result=subprocess.run([sys.executable,'-m','unittest','test_checkpoint_staging.CheckpointStaging.test_actual_path_limited_commit_preserves_unrelated_index'],cwd=REPO,env=env,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(sentinel.exists(),'Offline fixture tests executed caller Git hooks')
