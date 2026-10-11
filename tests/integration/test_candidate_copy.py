import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'unit'))
from support import REPO, run, git_snapshot

class CandidateCopy(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='copy-test-'); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'project space'; self.root.mkdir()
        for args in (['init','-q'],['config','user.email','fixture@example.invalid'],['config','user.name','Fixture']):
            self.assertEqual(run(['git','-C',self.root,*args]).returncode,0)
        (self.root/'code.py').write_text('value=2\n')
        (self.root/'test.py').write_text('from code import value\nassert value==2, "candidate value"\n')
        run(['git','-C',self.root,'add','code.py','test.py']); run(['git','-C',self.root,'commit','-qm','fixture'])
        (self.root/'code.py').write_text('value=3\n')
        (self.root/'test.py').write_text('from code import value\nassert value==3, "candidate value"\n')
        (self.root/'failure.py').write_text('from code import value\nassert value != 2, "failure path"\n')
        self.manifest=Path(self.temp.name)/'paths0'
        self.manifest.write_bytes(b'code.py\0test.py\0failure.py\0')

    def copy(self,env=None,timeout=15):
        return run(['/bin/bash',REPO/'scripts/itworks-test-copy.sh',self.root,self.manifest],env=env,timeout=timeout)

    def test_dirty_candidate_mutation_restore_and_original_identity(self):
        before=git_snapshot(self.root)
        result=self.copy(); self.assertEqual(result.returncode,0,result.stderr)
        copied=Path(result.stdout.strip()); self.addCleanup(shutil.rmtree,copied.parent)
        self.assertEqual(run([sys.executable,'-B','test.py'],cwd=copied).returncode,0)
        self.assertEqual(run([sys.executable,'-B','failure.py'],cwd=copied).returncode,0)
        original=(copied/'code.py').read_bytes(); (copied/'code.py').write_text('value=2\n')
        red=run([sys.executable,'-B','test.py'],cwd=copied)
        self.assertNotEqual(red.returncode,0); self.assertIn('AssertionError: candidate value',red.stderr)
        (copied/'code.py').write_bytes(original)
        self.assertEqual(run([sys.executable,'-B','test.py'],cwd=copied).returncode,0)
        self.assertEqual(git_snapshot(self.root),before)

    def test_reject_paths_and_symlinks(self):
        sentinel=Path(self.temp.name)/'sentinel'; sentinel.write_text('untouched')
        (self.root/'link').symlink_to(sentinel)
        for content in (b'../sentinel\0',b'link\0',b'code.py\0code.py\0',b'code.py',b'.git/config\0',b'/tmp/x\0'):
            self.manifest.write_bytes(content)
            result=self.copy(); self.assertNotEqual(result.returncode,0); self.assertEqual(result.stdout,'')
        self.assertEqual(sentinel.read_text(),'untouched')

    def test_source_change_and_copy_corruption_fail_closed(self):
        for destination in ('source','copy'):
            with self.subTest(destination=destination):
                bins=Path(self.temp.name)/('bin-'+destination); bins.mkdir()
                wrapper=bins/'cp'
                mutation='printf changed >> "$COPY_SOURCE/code.py"' if destination=='source' else 'printf changed >> "${@: -1}"'
                wrapper.write_text('#!/bin/bash\n'+shutil.which('cp')+' "$@"\n'+mutation+'\n')
                wrapper.chmod(0o755)
                result=self.copy({'PATH':str(bins)+os.pathsep+os.environ['PATH'],'COPY_SOURCE':str(self.root)})
                self.assertNotEqual(result.returncode,0); self.assertEqual(result.stdout,'')

    def test_missing_dependency_is_infrastructure_not_red(self):
        self.manifest.write_bytes(b'test.py\0')
        result=self.copy(); self.assertEqual(result.returncode,0,result.stderr)
        copied=Path(result.stdout.strip()); self.addCleanup(shutil.rmtree,copied.parent)
        result=run([sys.executable,'-B','test.py'],cwd=copied)
        self.assertNotEqual(result.returncode,0); self.assertIn('ImportError',result.stderr)
        self.assertNotIn('AssertionError: candidate value',result.stderr)

    def test_interruption_after_copied_mutation_preserves_source(self):
        import time
        before=git_snapshot(self.root)
        result=self.copy(); self.assertEqual(result.returncode,0,result.stderr)
        copied=Path(result.stdout.strip()); self.addCleanup(shutil.rmtree,copied.parent)
        script="from pathlib import Path; import time; Path('code.py').write_text('value=2\\n'); Path('ready').touch(); time.sleep(30)"
        child=subprocess.Popen([sys.executable,'-c',script],cwd=copied,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            deadline=time.monotonic()+5
            while not (copied/'ready').exists() and time.monotonic()<deadline:
                time.sleep(0.01)
            self.assertTrue((copied/'ready').exists(),'mutation child failed to start')
            child.terminate(); child.communicate(timeout=5)
            self.assertNotEqual(child.returncode,0)
            self.assertEqual(git_snapshot(self.root),before)
        finally:
            if child.poll() is None:
                child.kill(); child.communicate()

    def test_hash_failure_never_publishes_copy_identity(self):
        before=git_snapshot(self.root)
        bins=Path(self.temp.name)/'hash-bin';bins.mkdir()
        shim=bins/'shasum';shim.write_text('#!/bin/bash\nexit 42\n');shim.chmod(0o700)
        result=self.copy({'PATH':str(bins)+os.pathsep+os.environ['PATH']})
        if result.returncode==0:
            self.addCleanup(shutil.rmtree,Path(result.stdout.strip()).parent)
        self.assertNotEqual(result.returncode,0,'Failed hash command must invalidate identity')
        self.assertEqual(result.stdout,'')
        self.assertEqual(git_snapshot(self.root),before)

    def test_option_like_relative_path(self):
        (self.root/'-odd').mkdir();(self.root/'-odd/source.txt').write_text('candidate\n')
        self.manifest.write_bytes(b'-odd/source.txt\0')
        result=self.copy()
        self.assertEqual(result.returncode,0,result.stderr)
        copied=Path(result.stdout.strip());self.addCleanup(shutil.rmtree,copied.parent)
        self.assertEqual((copied/'-odd/source.txt').read_text(),'candidate\n')

    def test_each_hash_backend_failure_and_malformed_output_cleans_owned_temp(self):
        before=git_snapshot(self.root)
        for backend in ('shasum','sha256sum'):
            for label,body in (('failure','exit 42'), ('false-success',"printf 'not-a-digest\\n'"), ('failed-valid-output',"printf '%064d\\n' 0; exit 42")):
                with self.subTest(backend=backend,label=label):
                    bins=Path(self.temp.name)/(backend+'-'+label);bins.mkdir()
                    # Explicit tool PATH forces each backend without redefining HOME.
                    for tool in ('awk','mktemp','rm','mkdir','stat','sort','mv','git','cp','cmp','dirname'):
                        (bins/tool).symlink_to(shutil.which(tool))
                    shim=bins/backend;shim.write_text('#!/bin/bash\n'+body+'\n');shim.chmod(0o700)
                    private_tmp=Path(self.temp.name)/(backend+'-'+label+'-tmp');private_tmp.mkdir()
                    result=self.copy({'PATH':str(bins),'TMPDIR':str(private_tmp)})
                    if result.returncode==0:
                        self.addCleanup(shutil.rmtree,Path(result.stdout.strip()).parent)
                    self.assertNotEqual(result.returncode,0,'failed or malformed hash cannot establish identity')
                    self.assertEqual(result.stdout,'')
                    self.assertEqual(list(private_tmp.iterdir()),[],'owned incomplete copy must be cleaned')
                    self.assertEqual(git_snapshot(self.root),before)

    def test_real_sha256sum_fallback_matches_copied_identity(self):
        backend=shutil.which('sha256sum')
        if not backend:
            self.skipTest('NOT RUN: real sha256sum unavailable on this platform')
        bins=Path(self.temp.name)/'real-sha256-bin';bins.mkdir()
        for tool in ('awk','mktemp','rm','mkdir','stat','sort','mv','git','cp','cmp'):
            (bins/tool).symlink_to(shutil.which(tool))
        (bins/'sha256sum').symlink_to(backend)
        before=git_snapshot(self.root)
        result=self.copy({'PATH':str(bins)})
        self.assertEqual(result.returncode,0,result.stderr)
        copied=Path(result.stdout.strip());self.addCleanup(shutil.rmtree,copied.parent)
        self.assertEqual((copied/'code.py').read_bytes(),(self.root/'code.py').read_bytes())
        self.assertEqual((copied.parent/'before').read_bytes(),(copied.parent/'copied').read_bytes())
        self.assertEqual(git_snapshot(self.root),before)

    def test_git_fsmonitor_cannot_mutate_source_during_identity(self):
        monitor=Path(self.temp.name)/'monitor.sh'
        monitor.write_text('#!/bin/bash\nprintf mutated > "$ITWORKS_MONITOR_TARGET"\nprintf "token\\0"\n');monitor.chmod(0o700)
        run(['git','-C',self.root,'config','core.fsmonitor',str(monitor)])
        before=(self.root/'code.py').read_bytes()
        result=self.copy({'ITWORKS_MONITOR_TARGET':str(self.root/'code.py')})
        if result.returncode==0:self.addCleanup(shutil.rmtree,Path(result.stdout.strip()).parent)
        self.assertEqual((self.root/'code.py').read_bytes(),before,'Read-only identity ran source-mutating fsmonitor')
        self.assertEqual(result.returncode,0,result.stderr)

    def test_git_clean_and_process_filters_block_before_source_mutation(self):
        for kind in ('clean','process'):
            with self.subTest(kind=kind):
                script=Path(self.temp.name)/(kind+'-filter.sh')
                script.write_text('#!/bin/bash\nprintf mutated > "$ITWORKS_FILTER_TARGET"\n'+('cat\n' if kind=='clean' else 'exit 1\n'))
                script.chmod(0o700)
                (self.root/'.gitattributes').write_text('code.py filter=unsafe\n')
                self.assertEqual(run(['git','-C',self.root,'config','filter.unsafe.'+kind,str(script)]).returncode,0)
                (self.root/'code.py').write_text('value=3\n')
                source_stat=(self.root/'code.py').stat()
                os.utime(self.root/'code.py',ns=(source_stat.st_atime_ns,source_stat.st_mtime_ns+10000000000))
                before=(self.root/'code.py').read_bytes()
                private_tmp=Path(self.temp.name)/(kind+'-temp');private_tmp.mkdir()
                result=self.copy({'ITWORKS_FILTER_TARGET':str(self.root/'code.py'),'TMPDIR':str(private_tmp)},timeout=45)
                if result.returncode==0:self.addCleanup(shutil.rmtree,Path(result.stdout.strip()).parent)
                self.assertEqual((self.root/'code.py').read_bytes(),before,'read-only identity invoked '+kind+' filter')
                self.assertNotEqual(result.returncode,0,'configured executable filters require explicit isolation')
                self.assertEqual(result.stdout,'')
                self.assertNotIn(str(script),result.stderr,'diagnostic must not print configured command values')
                self.assertEqual(list(private_tmp.glob('itworks-copy.*')),[])
                run(['git','-C',self.root,'config','--unset','filter.unsafe.'+kind])

    def test_empty_or_invalid_mode_cannot_establish_copy_identity(self):
        before=git_snapshot(self.root)
        for label,output in (('empty',''),('non-octal','89'),('too-long','100755')):
            with self.subTest(mode=label):
                bins=Path(self.temp.name)/('mode-'+label);bins.mkdir()
                shim=bins/'stat';shim.write_text("#!/bin/bash\nprintf '%s' '"+output+"'\n");shim.chmod(0o700)
                result=self.copy({'PATH':str(bins)+os.pathsep+os.environ['PATH']})
                if result.returncode==0:self.addCleanup(shutil.rmtree,Path(result.stdout.strip()).parent)
                self.assertNotEqual(result.returncode,0,'empty or malformed mode cannot establish identity')
                self.assertEqual(result.stdout,'')
                self.assertEqual(git_snapshot(self.root),before)
