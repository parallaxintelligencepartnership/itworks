"""Mock CLI boundary tests; no real model, account, plugin or network."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
HARNESS=ROOT/'tests/pressure/harness'

class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='itworks-harness-test-')
        self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name)
        self.bin=self.work/'bin';self.bin.mkdir()
        (self.bin/'claude').symlink_to(ROOT/'tests/fixtures/harness/mock-cli.py')
        (self.bin/'date').write_text('#!/bin/sh\nprintf \'20261011-120000\\n\'\n')
        (self.bin/'date').chmod(0o755)
        self.config=self.work/'config.json'
        self.record=self.work/'calls.jsonl'
        self.results=self.work/'results'
        self.env={**os.environ, 'PATH':str(self.bin)+os.pathsep+os.environ['PATH'],
            'ITWORKS_HARNESS_MODE':'mock','ITWORKS_MOCK_CONFIG':str(self.config),
            'ITWORKS_RESULTS_DIR':str(self.results),'ITWORKS_TIMEOUT_SECONDS':'2',
            'ITWORKS_MAX_REQUESTS':'12'}
        self.configure()
    def configure(self,**kw):
        self.config.write_text(json.dumps({'record':str(self.record),**kw}))
    def run_case(self):
        return subprocess.run(['bash',str(HARNESS/'run-case.sh'),'case-kickoff-complete','identity-marker','1'],
            cwd=ROOT, env=self.env, capture_output=True,text=True,timeout=20)
    def calls(self):
        return [json.loads(line) for line in self.record.read_text().splitlines()]
    def artifacts(self):
        return sorted(self.results.glob('run-*'))
    def test_blank_is_incomplete(self):
        self.configure(reply=' \t\n')
        result=self.run_case()
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertEqual(len(self.calls()),1)
    def test_cwd_and_complete_instructions(self):
        result=self.run_case();self.assertEqual(result.returncode,0,result.stderr)
        call=self.calls()[0]
        self.assertNotEqual(Path(call['cwd']), ROOT)
        prompt=call['argv'][call['argv'].index('-p')+1]
        self.assertIn((ROOT/'skills/project-kickoff/SKILL.md').read_text(),prompt)
        self.assertIn((ROOT/'references/state-format.md').read_text(),prompt)
        self.assertNotIn('Judge-only golden fragments',prompt)
        self.assertIn('--tools',call['argv'])
        self.assertEqual(call['argv'][call['argv'].index('--tools')+1],'')
    def test_unique_artifacts_and_blind_export(self):
        for _ in range(2):self.assertEqual(self.run_case().returncode,0)
        self.assertEqual(len(list(self.results.iterdir())),2)
        artifacts=self.artifacts();self.assertEqual(len(artifacts),2)
        for directory in artifacts:
            manifest=json.loads((directory/'manifest.json').read_text())
            self.assertEqual(manifest['status'],'CAPTURED')
            self.assertEqual(manifest['resolved_model'],'unknown')
        destination=self.work/'judge'
        result=subprocess.run([sys.executable,str(HARNESS/'export-judge.py'),str(artifacts[0]),str(destination)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn('identity-marker',(destination/'transcript.txt').read_text())
        self.assertEqual(json.loads((destination/'score.json').read_text())['verdict'],'INCONCLUSIVE')
