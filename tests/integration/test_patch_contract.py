"""Package-copy qualification with a PATH deliberately lacking Python and host CLIs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
from support import REPO, tree_snapshot, git_snapshot

class PatchPackageContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='itworks-patch-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.package=self.root/'candidate package'
        for directory in ('scripts','hooks','.claude-plugin'):
            shutil.copytree(REPO/directory,self.package/directory)
        self.bin=self.root/'runtime-bin';self.bin.mkdir()
        for name in ('bash','awk','find','mktemp','rm','dirname','grep','sed','head','tr','wc',
                     'shasum','sha256sum','stat','sort','mv','mkdir','cp','cmp','git'):
            actual=shutil.which(name)
            if actual:(self.bin/name).symlink_to(actual)
        self.env={**os.environ,'PATH':str(self.bin),'GIT_CONFIG_NOSYSTEM':'1',
                  'GIT_CONFIG_GLOBAL':os.devnull,'GIT_OPTIONAL_LOCKS':'0'}
        self.package_before=tree_snapshot(self.package)
    def command(self,*args,**kw):
        result=subprocess.run([str(a) for a in args],env=self.env,capture_output=True,text=True,timeout=20,**kw)
        self.assertEqual(tree_snapshot(self.package),self.package_before)
        return result
    def materialize(self,name):
        target=self.root/('Café candidate = space '+name)
        shutil.copytree(REPO/'tests/fixtures/compatibility'/name,target)
        return target
    def test_real_packaged_modes_and_legacy_bytes_without_python(self):
        self.assertFalse(shutil.which('python',path=str(self.bin)))
        self.assertFalse(shutil.which('python3',path=str(self.bin)))
        self.assertFalse(shutil.which('claude',path=str(self.bin)))
        self.assertFalse(shutil.which('gh',path=str(self.bin)))
        for name in ('v1-minimal','v2-missing-map','v3-valid','v3-crlf','v3-no-final-newline','v3-archive'):
            with self.subTest(name=name):
                target=self.materialize(name);before=tree_snapshot(target)
                for operation in ('check','gate','counts'):
                    result=self.command('/bin/bash',self.package/'scripts/itworks-state.sh',operation,target)
                    self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                    self.assertTrue(result.stdout.startswith('FORMAT\t1\n'))
                    self.assertEqual(result.stdout.splitlines()[-1].split('\t')[0],'SUMMARY')
                    if operation=='counts':self.assertEqual(result.stdout.count('COUNT\t'),5)
                    self.assertEqual(tree_snapshot(target),before)
                result=self.command('/bin/bash',self.package/'scripts/itworks-lint.sh',target)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(tree_snapshot(target),before)
    def test_failed_or_blocked_counts_never_publish_payload(self):
        for name,status in [('v3-corrupt-critical',1),('v3-ambiguous-acceptance',2)]:
            target=self.materialize(name);before=tree_snapshot(target)
            result=self.command('/bin/bash',self.package/'scripts/itworks-state.sh','counts',target)
            self.assertEqual(result.returncode,status,result.stdout)
            self.assertNotIn('COUNT\t',result.stdout)
            self.assertEqual(tree_snapshot(target),before)
    def test_missing_awk_and_unreadable_state_fail(self):
        target=self.materialize('v3-valid')
        profile=target/'.itworks/PROFILE.md';profile.chmod(0)
        self.addCleanup(lambda:profile.chmod(0o600) if profile.exists() else None)
        result=self.command('/bin/bash',self.package/'scripts/itworks-state.sh','counts',target)
        if os.geteuid()!=0:
            self.assertEqual(result.returncode,1)
            self.assertNotIn('COUNT\t',result.stdout)
        profile.chmod(0o600)
        (self.bin/'awk').unlink()
        result=self.command('/bin/bash',self.package/'scripts/itworks-state.sh','counts',target)
        self.assertEqual(result.returncode,1)
        self.assertNotIn('COUNT\t',result.stdout)
    def test_disabled_packaged_hook_without_python(self):
        target=self.materialize('v3-valid');before=tree_snapshot(target)
        self.env.update(ITWORKS_DISABLE='1',CLAUDE_PROJECT_DIR=str(target))
        result=self.command('/bin/bash',self.package/'hooks/session-start.sh')
        self.assertEqual((result.returncode,result.stdout),(0,''))
        self.assertEqual(tree_snapshot(target),before)
    def test_candidate_copy_without_python_preserves_git_identity(self):
        target=self.root/'dirty candidate';target.mkdir()
        source=target/'source.txt';source.write_text('committed\n')
        commands=[['init','-q'],['add','source.txt'],['-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','core.hooksPath=/dev/null','commit','-qm','fixture']]
        for command in commands:
            result=self.command('git','-C',target,*command)
            self.assertEqual(result.returncode,0,result.stderr)
        source.write_text('dirty candidate\n');(target/'extra.txt').write_text('untracked\n')
        manifest=self.root/'paths0';manifest.write_bytes(b'source.txt\0extra.txt\0')
        before=git_snapshot(target)
        result=self.command('/bin/bash',self.package/'scripts/itworks-test-copy.sh',target,manifest)
        self.assertEqual(result.returncode,0,result.stderr)
        copied=Path(result.stdout.strip())
        self.addCleanup(lambda:shutil.rmtree(copied.parent))
        self.assertEqual((copied/'source.txt').read_bytes(),source.read_bytes())
        self.assertEqual((copied/'extra.txt').read_text(),'untracked\n')
        self.assertEqual(git_snapshot(target),before)
