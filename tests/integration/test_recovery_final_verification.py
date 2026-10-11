"""Fault after staged writes must not compare two failed manifests as success."""
import os
from pathlib import Path
import shutil
import unittest
import test_state_recovery as recovery_fixture
from support import tree_snapshot

class RecoveryFinalVerification(unittest.TestCase):
    def test_two_failed_final_inventories_do_not_report_applied(self):
        fixture=recovery_fixture.Recovery(methodName='runTest');fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.prepare()
        bins=fixture.base/'fault-bin';bins.mkdir()
        marker=fixture.base/'written'
        cp=bins/'cp'
        cp.write_text('#!/bin/bash\n/bin/cp "$@" || exit $?\nfor arg in "$@"; do\n case "$arg" in "$STAGING/"*) : > "$FINAL_STAT_FAILURE";; esac\ndone\n')
        stat=bins/'stat'
        stat.write_text('#!/bin/bash\n[ ! -f "$FINAL_STAT_FAILURE" ] || exit 42\nexec '+shutil.which('stat')+' "$@"\n')
        cp.chmod(0o700);stat.chmod(0o700)
        fixture.env.update(PATH=str(bins)+os.pathsep+os.environ['PATH'],FINAL_STAT_FAILURE=str(marker))
        result=fixture.apply()
        self.assertTrue(marker.exists(),'fault must activate after staged write')
        self.assertNotEqual(result.returncode,0,'Failed final inventories cannot prove application success')
        self.assertNotIn('Applied;',result.stdout)
        self.assertEqual(tree_snapshot(fixture.backup/'payload'),fixture.original)
