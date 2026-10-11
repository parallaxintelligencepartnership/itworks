"""Run actual documented shell blocks/helper on disposable synthetic state."""
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
from support import REPO,run,tree_snapshot

FIXTURES=REPO/'tests/fixtures/compatibility'
HELPER=REPO/'scripts/itworks-recovery.sh'
BLOCKS=dict(re.findall(r'<!-- recovery:([^ ]+) -->\s*```sh\n(.*?)```',(REPO/'references/upgrade-recovery.md').read_text(),re.S))


class Recovery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='itworks-recovery-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve()
        self.project=self.base/'project with spaces';shutil.copytree(FIXTURES/'v1-minimal',self.project)
        self.backup=self.base/'backup';self.stage=self.base/'stage';self.cache=self.base/'cache';self.cache.mkdir()
        self.env={'PROJECT':str(self.project),'PLUGIN':str(REPO),'INSTALLED_CACHE':str(self.cache),'BACKUP':str(self.backup),'STAGING':str(self.stage),'RESTORED':str(self.base/'restored')}
        self.original=tree_snapshot(self.project)

    def block(self,name,expected=0):
        result=run(['bash','-c',BLOCKS[name]],env=self.env)
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        return result

    def prepare(self):
        self.block('snapshot');self.block('staging-copy')
        profile=self.stage/'.itworks/PROFILE.md'
        with profile.open('a') as stream:
            stream.write('\nformat_version: 3\nlast_audit: none\n  llm-security: 0\n')
        shutil.copy2(FIXTURES/'v3-valid/.itworks/MAP.md',self.stage/'.itworks/MAP.md')

    def apply(self):
        return run(['bash',HELPER,'apply',self.project,self.backup,self.stage,REPO],env=self.env)

    def shim(self,body):
        bindir=self.base/'bin';bindir.mkdir(exist_ok=True)
        script=bindir/'cp'
        script.write_text('#!/usr/bin/env bash\nset -eu\n'+body+'\nexec /bin/cp "$@"\n');script.chmod(0o700)
        self.env.update(PATH=str(bindir)+os.pathsep+os.environ['PATH'],TEST_PROJECT=str(self.project),TEST_COUNTER=str(self.base/'counter'))

    def test_runbook_snapshot_stage_verify_restore_preserve_bytes(self):
        self.prepare();self.block('verify-before-write');self.block('restore-to-empty-directory')
        self.assertEqual(tree_snapshot(self.project),self.original)
        self.assertEqual(tree_snapshot(self.base/'restored'),self.original)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)
        self.assertEqual(self.backup.stat().st_mode&0o777,0o700)
        original_quote=(self.project/'.itworks/REVIEWS.md').read_bytes()
        result=self.apply();self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual((self.project/'.itworks/REVIEWS.md').read_bytes(),original_quote)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)

    def test_crlf_no_newline_and_critical_roundtrip(self):
        for name in ('v3-crlf','v3-no-final-newline','v3-corrupt-critical','v3-ambiguous-acceptance'):
            with self.subTest(name=name):
                project=self.base/name;shutil.copytree(FIXTURES/name,project)
                backup=self.base/(name+'-backup');restored=self.base/(name+'-restored')
                result=run(['bash',HELPER,'snapshot',project,backup,REPO,self.cache]);self.assertEqual(result.returncode,0,result.stderr)
                result=run(['bash',HELPER,'restore-to-empty',backup,restored]);self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(tree_snapshot(project),tree_snapshot(restored))

    def test_reject_internal_existing_and_symlink_destinations(self):
        for backup in (self.project/'backup',REPO/'never-create-test-backup',self.cache/'backup'):
            result=run(['bash',HELPER,'snapshot',self.project,backup,REPO,self.cache])
            self.assertNotEqual(result.returncode,0);self.assertFalse(backup.exists())
        self.block('snapshot');saved=tree_snapshot(self.backup);self.block('snapshot',1)
        self.assertEqual(tree_snapshot(self.backup),saved)
        (self.project/'.itworks/escape').symlink_to(self.cache,target_is_directory=True)
        result=run(['bash',HELPER,'snapshot',self.project,self.base/'linked-backup',REPO,self.cache])
        self.assertNotEqual(result.returncode,0);self.assertFalse((self.base/'linked-backup').exists())

    def test_copy_capacity_failure_prevents_project_writes(self):
        self.shim('printf "simulated ENOSPC\\n" >&2; exit 1')
        self.block('snapshot',1)
        self.assertEqual(tree_snapshot(self.project),self.original)
        self.assertFalse((self.backup/'VERIFIED').exists())

    def test_concurrent_change_aborts_without_overwriting(self):
        self.prepare()
        path=self.project/'.itworks/DECISIONS.md';path.write_bytes(path.read_bytes()+b'\nNew user note\n')
        concurrent=tree_snapshot(self.project)
        self.block('verify-before-write',1)
        result=self.apply();self.assertNotEqual(result.returncode,0)
        self.assertEqual(tree_snapshot(self.project),concurrent)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)

    def test_tampered_backup_never_restores(self):
        self.block('snapshot')
        path=self.backup/'payload/.itworks/REVIEWS.md';path.write_bytes(b'wrong')
        self.block('restore-to-empty-directory',1)
        self.assertFalse((self.base/'restored').exists())
        self.assertEqual(tree_snapshot(self.project),self.original)

    def test_malformed_acceptance_staging_remains_unresolved(self):
        self.prepare()
        shutil.copy2(FIXTURES/'v3-malformed-acceptance/.itworks/REVIEWS.md',self.stage/'.itworks/REVIEWS.md')
        result=self.apply();self.assertNotEqual(result.returncode,0)
        self.assertEqual(tree_snapshot(self.project),self.original)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)

    def test_partial_replacement_rolls_back_and_keeps_failed_candidate(self):
        self.prepare()
        self.shim('''last=${!#}
case "$last" in "$TEST_PROJECT/"*)
 n=0; [ ! -f "$TEST_COUNTER" ] || n=$(cat "$TEST_COUNTER"); n=$((n+1)); echo "$n" > "$TEST_COUNTER"
 [ "$n" != 2 ] || { printf 'simulated permission failure\\n' >&2; exit 1; };; esac''')
        result=self.apply();self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('Original state restored and verified',result.stderr)
        self.assertEqual(tree_snapshot(self.project),self.original)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)
        self.assertTrue(list(self.base.glob('itworks-failed.*')))

    def test_restore_failure_retains_independent_evidence(self):
        self.prepare()
        self.shim('''last=${!#}
case "$last" in "$TEST_PROJECT/"*) printf 'simulated write denial\\n' >&2; exit 1;; esac''')
        result=self.apply();self.assertNotEqual(result.returncode,0)
        self.assertIn('manual recovery required',result.stderr)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)
        self.assertTrue(self.stage.exists())
        self.assertTrue(list(self.base.glob('itworks-failed.*')))
        self.assertTrue(list(self.base.glob('itworks-restore.*')))


    def test_staging_failure_and_restore_rehearsal_prevent_writes(self):
        self.block('snapshot')
        self.shim('printf "simulated capacity failure\\n" >&2; exit 1')
        self.block('staging-copy',1)
        self.assertEqual(tree_snapshot(self.project),self.original)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)

    def test_post_write_lint_failure_restores_original(self):
        self.prepare()
        bindir=self.base/'bin';bindir.mkdir()
        script=bindir/'bash'
        script.write_text('#!/bin/bash\ncase "${1:-}" in */itworks-lint.sh) [ "${2:-}" != "$TEST_PROJECT" ] || exit 1;; esac\nexec /bin/bash "$@"\n')
        script.chmod(0o700)
        self.env.update(PATH=str(bindir)+os.pathsep+os.environ['PATH'],TEST_PROJECT=str(self.project))
        result=self.apply();self.assertNotEqual(result.returncode,0)
        self.assertIn('Original state restored and verified',result.stderr)
        self.assertEqual(tree_snapshot(self.project),self.original)
        self.assertEqual(tree_snapshot(self.backup/'payload'),self.original)

    def test_staging_inside_project_and_state_symlink_rejected(self):
        self.block('snapshot')
        self.env['STAGING']=str(self.project/'unsafe-stage')
        self.block('staging-copy',1)
        self.assertFalse((self.project/'unsafe-stage').exists())
        state=self.project/'.itworks';state.rename(self.base/'external-state')
        state.symlink_to(self.base/'external-state',target_is_directory=True)
        result=run(['bash',HELPER,'snapshot',self.project,self.base/'symlink-backup',REPO,self.cache])
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.base/'symlink-backup').exists())

    def test_shipped_history_is_restored_after_partial_replacement(self):
        (self.project/'SHIPPED.md').write_bytes(b'# Historical ship\r\n## Accepted risks\r\nOriginal user history without final newline')
        self.original=tree_snapshot(self.project)
        self.test_partial_replacement_rolls_back_and_keeps_failed_candidate()
        self.assertEqual((self.project/'SHIPPED.md').read_bytes(),(self.backup/'payload/SHIPPED.md').read_bytes())

    def test_identity_metadata_missing_duplicate_symlink_and_project_mismatch(self):
        import hashlib
        self.prepare()
        identity=self.backup/'identity.txt';original=identity.read_bytes()
        for damaged in (b'',original+original.splitlines(keepends=True)[0],original.replace(b'cache=',b'unknown=')):
            with self.subTest(damaged=damaged[:20]):
                identity.write_bytes(damaged)
                (self.backup/'identity.sha256').write_text(hashlib.sha256(damaged).hexdigest()+'\n')
                self.block('restore-to-empty-directory',1)
                self.assertFalse((self.base/'restored').exists())
        identity.write_bytes(original)
        (self.backup/'identity.sha256').write_text(hashlib.sha256(original).hexdigest()+'\n')
        other=self.base/'other-project';shutil.copytree(self.project,other)
        result=run(['bash',HELPER,'verify-before-write',other,self.backup]);self.assertNotEqual(result.returncode,0)
        result=run(['bash',HELPER,'apply',other,self.backup,self.stage,REPO]);self.assertNotEqual(result.returncode,0)
        self.assertEqual(tree_snapshot(other),self.original)
        external=self.base/'identity-original';identity.rename(external);identity.symlink_to(external)
        self.block('restore-to-empty-directory',1)
        self.assertFalse((self.base/'restored').exists())

    def test_restore_available_after_original_source_disappears(self):
        self.block('snapshot')
        self.project.rename(self.base/'moved-original')
        self.block('restore-to-empty-directory')
        self.assertEqual(tree_snapshot(self.base/'restored'),self.original)

    def test_unsafe_overwrite_counterexample_is_detected(self):
        self.prepare()
        path=self.project/'.itworks/DECISIONS.md';path.write_bytes(b'concurrent user note')
        expected=tree_snapshot(self.project)
        # Deliberately unsafe implementation on a disposable copy. This assertion
        # is the intended RED: blindly restoring would erase concurrent notes.
        shutil.copy2(self.backup/'payload/.itworks/DECISIONS.md',path)
        with self.assertRaises(AssertionError):
            self.assertEqual(tree_snapshot(self.project),expected)

class RecoveryReview(Recovery):
    def test_snapshot_does_not_refresh_source_index(self):
        import hashlib
        for cmd in (['git','init','-q'],['git','config','user.email','fixture@example.invalid'],['git','config','user.name','Fixture'],['git','add','--','.'],['git','commit','-qm','fixture']):
            self.assertEqual(run(cmd,cwd=self.project).returncode,0)
        path=self.project/'.itworks/PROJECT.md'
        os.utime(path,(path.stat().st_atime+5,path.stat().st_mtime+5))
        index=self.project/'.git/index';before=index.read_bytes()
        self.block('snapshot')
        self.assertEqual(index.read_bytes(),before)

    def test_truncated_identity_cannot_bypass_external_destination(self):
        self.block('snapshot')
        (self.backup/'identity.txt').write_text('')
        self.env['STAGING']=str(self.project/'unsafe-stage')
        self.block('staging-copy',1)
        self.assertFalse((self.project/'unsafe-stage').exists())

    def test_failed_or_empty_hash_cannot_verify_backup(self):
        bins=self.base/'hash-bin';bins.mkdir()
        for output in ('exit 42','exit 0','echo not-a-digest'):
            with self.subTest(output=output):
                shim=bins/'shasum';shim.write_text('#!/bin/bash\n'+output+'\n');shim.chmod(0o700)
                backup=self.base/('hash-backup-'+str(len(list(self.base.glob('hash-backup-*')))))
                result=run(['/bin/bash',HELPER,'snapshot',self.project,backup,REPO,self.cache],env={'PATH':str(bins)+os.pathsep+os.environ['PATH']})
                self.assertNotEqual(result.returncode,0,'Hash failure cannot establish verified backup')
                self.assertFalse((backup/'VERIFIED').exists())
                self.assertEqual(tree_snapshot(self.project),self.original)

    def test_failed_identity_hash_cannot_match_empty_metadata(self):
        self.block('snapshot')
        (self.backup/'identity.sha256').write_text('')
        bins=self.base/'identity-hash-bin';bins.mkdir()
        shim=bins/'shasum'
        shim.write_text('#!/bin/bash\ntmp=$(mktemp)\ntrap \'rm -f "$tmp"\' EXIT\ncat > "$tmp"\nif head -1 "$tmp" | grep -q "^project="; then exit 42; fi\n/usr/bin/shasum "$@" "$tmp"\n')
        shim.chmod(0o700)
        result=run(['/bin/bash',HELPER,'verify-before-write',self.project,self.backup],env={'PATH':str(bins)+os.pathsep+os.environ['PATH']})
        self.assertNotEqual(result.returncode,0,'Failed metadata hash cannot equal an empty stored hash')

    def test_failed_mode_probe_cannot_verify_backup(self):
        bins=self.base/'stat-bin';bins.mkdir()
        shim=bins/'stat';shim.write_text('#!/bin/bash\nexit 42\n');shim.chmod(0o700)
        result=run(['/bin/bash',HELPER,'snapshot',self.project,self.backup,REPO,self.cache],env={'PATH':str(bins)+os.pathsep+os.environ['PATH']})
        self.assertNotEqual(result.returncode,0,'Failed stat cannot prove preserved modes')
        self.assertFalse((self.backup/'VERIFIED').exists())
        self.assertEqual(tree_snapshot(self.project),self.original)

    def git_fixture(self):
        for args in (['init','-q'],['config','user.email','fixture@example.invalid'],['config','user.name','Fixture']):
            self.assertEqual(run(['git',*args],cwd=self.project).returncode,0)
        (self.project/'data.txt').write_text('original\n')
        (self.project/'.gitattributes').write_text('data.txt filter=recovery-probe\n')
        self.assertEqual(run(['git','add','.'],cwd=self.project).returncode,0)
        self.assertEqual(run(['git','commit','-qm','synthetic state'],cwd=self.project).returncode,0)
        (self.project/'data.txt').write_text('changed!\n')
        data=self.project/'data.txt';os.utime(data,(data.stat().st_atime+5,data.stat().st_mtime+5))

    def test_git_clean_and_process_filters_are_never_executed(self):
        import shlex
        self.git_fixture()
        for kind in ('clean','process'):
            with self.subTest(kind=kind):
                marker=self.project/('filter-'+kind+'-ran')
                executable=self.base/('private-filter-'+kind)
                executable.write_text('#!/bin/bash\nprintf touched > '+shlex.quote(str(marker))+'\n'+('cat\n' if kind=='clean' else 'exit 1\n'))
                executable.chmod(0o700)
                key='filter.recovery-probe.'+kind
                command=shlex.quote(str(executable))
                self.assertEqual(run(['git','config',key,command],cwd=self.project).returncode,0)
                before=tree_snapshot(self.project)
                backup=self.base/('filter-'+kind+'-backup')
                result=run(['/bin/bash',HELPER,'snapshot',self.project,backup,REPO,self.cache])
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(marker.exists(),'Git filter executed during recovery identity inspection')
                self.assertFalse((backup/'VERIFIED').exists())
                self.assertEqual(tree_snapshot(self.project),before)
                self.assertNotIn(command,result.stdout+result.stderr)
                self.assertEqual(run(['git','config','--unset',key],cwd=self.project).returncode,0)

    def test_git_fsmonitor_is_disabled_without_index_changes(self):
        import shlex
        self.git_fixture()
        marker=self.project/'fsmonitor-ran'
        executable=self.base/'fsmonitor-hook'
        executable.write_text('#!/bin/bash\nprintf touched > '+shlex.quote(str(marker))+'\nprintf "synthetic-token\\0"\n')
        executable.chmod(0o700)
        self.assertEqual(run(['git','config','core.fsmonitor',str(executable)],cwd=self.project).returncode,0)
        before=tree_snapshot(self.project)
        result=run(['/bin/bash',HELPER,'snapshot',self.project,self.backup,REPO,self.cache])
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse(marker.exists(),'Git fsmonitor executed during recovery snapshot')
        self.assertEqual(tree_snapshot(self.project),before)
