"""Offline process isolation mechanics; expressly not real-host qualification."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
import test_harness as support

class SimulationIsolationTests(support.HarnessTests):
    def test_live_default_blocks_before_cli(self):
        self.env.pop('ITWORKS_HARNESS_MODE')
        result=self.run_case()
        self.assertEqual(result.returncode,69)
        self.assertIn('BLOCKED',result.stderr)
        self.assertFalse(self.record.exists())
        self.assertFalse(self.results.exists())
    def test_empty_and_underlying_error_preserve_partial_evidence(self):
        for config in ({'reply':''},{'reply':'partial stdout','stderr':'mock transport error','exit':42}):
            with self.subTest(config=config):
                self.configure(**config)
                result=self.run_case();self.assertEqual(result.returncode,1)
                directory=Path(result.stdout.strip())
                manifest=json.loads((directory/'manifest.json').read_text())
                self.assertEqual(manifest['status'],'INCOMPLETE')
                self.assertEqual(len(manifest['turns']),1)
                self.assertEqual(manifest['turns'][0]['exit_status'],config.get('exit',0))
                self.assertEqual((directory/'stdout-001.txt').read_text(),config['reply'])
                destination=self.work/('judge-'+directory.name)
                subprocess.run([sys.executable,str(support.HARNESS/'export-judge.py'),str(directory),str(destination)],check=True)
                self.assertEqual(json.loads((destination/'score.json').read_text())['verdict'],'INVALID_EVAL')
    def test_timeout_is_infrastructure_failure(self):
        self.configure(delay=2)
        self.env['ITWORKS_TIMEOUT_SECONDS']='0.1'
        result=self.run_case();self.assertEqual(result.returncode,1)
        manifest=json.loads((Path(result.stdout.strip())/'manifest.json').read_text())
        self.assertEqual(manifest['turns'][0]['exit_status'],124)
        self.assertEqual(manifest['status'],'INCOMPLETE')
    def test_environment_and_snapshots_are_separate(self):
        self.env['ANTHROPIC_API_KEY']='synthetic-do-not-forward'
        before=(support.ROOT/'tests/fixtures/harness/mock-cli.py').read_bytes()
        result=self.run_case();self.assertEqual(result.returncode,0,result.stderr)
        call=self.calls()[0]
        self.assertFalse(call['credential_present'])
        self.assertEqual(call['home'],os.environ.get('HOME'))
        self.assertNotEqual(call['cwd'],call['config_dir'])
        self.assertFalse(Path(call['cwd']).exists()) # Owned temporary workspace removed.
        directory=Path(result.stdout.strip())
        manifest=json.loads((directory/'manifest.json').read_text())
        for name,expected in manifest['input_hashes'].items():
            self.assertEqual(hashlib.sha256((directory/'inputs'/name).read_bytes()).hexdigest(),expected)
        self.assertEqual((support.ROOT/'tests/fixtures/harness/mock-cli.py').read_bytes(),before)
    def test_request_bound_prevents_invocation(self):
        self.env['ITWORKS_MAX_REQUESTS']='2'
        result=self.run_case();self.assertNotEqual(result.returncode,0)
        self.assertIn('bound',result.stderr)
        self.assertFalse(self.record.exists())
    def test_existing_evidence_and_judgment_never_overwritten(self):
        result=self.run_case();self.assertEqual(result.returncode,0)
        directory=Path(result.stdout.strip())
        before={str(p.relative_to(directory)):p.read_bytes() for p in directory.rglob('*') if p.is_file()}
        self.assertEqual(self.run_case().returncode,0)
        self.assertEqual(before,{str(p.relative_to(directory)):p.read_bytes() for p in directory.rglob('*') if p.is_file()})
        dest=self.work/'judge-once'
        cmd=[sys.executable,str(support.HARNESS/'export-judge.py'),str(directory),str(dest)]
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        (dest/'score.json').write_text('independent reviewer working')
        self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        self.assertEqual((dest/'score.json').read_text(),'independent reviewer working')
    def test_identity_in_reply_is_removed(self):
        self.configure(reply='I am IDENTITY-MARKER. Mock answer.')
        result=self.run_case();self.assertEqual(result.returncode,0)
        dest=self.work/'blind'
        subprocess.run([sys.executable,str(support.HARNESS/'export-judge.py'),result.stdout.strip(),str(dest)],check=True)
        self.assertNotIn('identity-marker',(dest/'transcript.txt').read_text().lower())
