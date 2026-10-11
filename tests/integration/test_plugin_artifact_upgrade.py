"""OFFLINE package replacement simulation, never a Claude updater claim."""
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
from support import run,tree_snapshot
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'support'))
from release_artifacts import REPO,RELEASE,materialize,candidate,hashes,extract_archive

FIXTURES=REPO/'tests/fixtures/compatibility'
MANIFEST=json.loads((FIXTURES/'manifest.json').read_text())


class ArtifactUpgrade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name)
        cls.old=cls.root/'release';materialize(RELEASE,cls.old)
        cls.patch=cls.root/'candidate';cls.identity=candidate(cls.patch)
        cls.expected=hashes(cls.patch)
        cls.version=json.loads((cls.patch/'.claude-plugin/plugin.json').read_text())['version']

    def setUp(self):
        self.temp_case=tempfile.TemporaryDirectory();self.addCleanup(self.temp_case.cleanup)
        self.case=Path(self.temp_case.name)
        self.selected=self.old

    def select(self,staged,expected,version):
        # A harness selection pointer, NOT a host installation/cache operation.
        if hashes(staged)!=expected:raise ValueError('staged artifact checksum mismatch')
        if json.loads((staged/'.claude-plugin/plugin.json').read_text())['version']!=version:
            raise ValueError('staged artifact version mismatch')
        for command in ('project-kickoff','project-resume','project-checkpoint','project-closeout','project-audit'):
            if not (staged/'skills'/command/'SKILL.md').is_file():raise ValueError('missing command')
            if not (staged/'commands'/(command.removeprefix('project-')+'.md')).is_file():raise ValueError('missing command wrapper')
        self.selected=staged

    def test_replacement_and_rollback_preserve_state_and_blocked_evidence(self):
        staged=self.case/'install-b';shutil.copytree(self.patch,staged)
        old_identity=hashes(self.old)
        self.select(staged,self.expected,self.version)
        self.assertEqual(self.selected,staged)
        hook=run(['bash',staged/'hooks/session-start.sh'],cwd=staged,env={'ITWORKS_DISABLE':'0','CLAUDE_PROJECT_DIR':str(staged),'CLAUDE_PLUGIN_ROOT':str(staged)})
        self.assertEqual(hook.returncode,0,hook.stderr)
        if not (Path.home()/'.config/itworks/disabled').exists():
            self.assertIn('itworks v'+self.version,hook.stdout)
        else:
            self.assertEqual(hook.stdout,'')
        for fixture in MANIFEST['cases']:
            with self.subTest(case=fixture['name']):
                project=self.case/fixture['name'];shutil.copytree(FIXTURES/fixture['name'],project)
                before=tree_snapshot(project)
                result=run(['bash',self.selected/'scripts/itworks-lint.sh',project])
                self.assertEqual(result.returncode,fixture['expected']['check']['exit_status'],result.stdout+result.stderr)
                self.assertEqual(tree_snapshot(project),before)
        project=self.case/'v3-ambiguous-acceptance'
        blocked=run(['bash',self.selected/'scripts/itworks-state.sh','gate',project])
        self.assertEqual(blocked.returncode,2)
        report=self.case/'retained-patch-blocked.txt';report.write_text(blocked.stdout)
        saved=report.read_bytes()
        self.select(self.old,old_identity,'1.0.0')
        downgraded=run(['bash',self.selected/'scripts/itworks-lint.sh',project])
        self.assertEqual(downgraded.returncode,0,'recorded old false pass')
        self.assertEqual(report.read_bytes(),saved)
        self.assertIn(b'B_ACCEPTANCE_LINK',saved)
        self.assertEqual(hashes(self.old),old_identity)

    def test_interrupted_extraction_and_wrong_hash_never_select_candidate(self):
        old_identity=hashes(self.old)
        # Valid tar with a deliberately incomplete payload models interruption
        # without confusing a corrupt test setup with the intended checksum RED.
        data=io.BytesIO()
        with tarfile.open(fileobj=data,mode='w') as archive:
            entry=tarfile.TarInfo('partial.txt');entry.size=7;archive.addfile(entry,io.BytesIO(b'partial'))
        staged=self.case/'partial-install';extract_archive(data.getvalue(),staged)
        with self.assertRaisesRegex(ValueError,'checksum'):
            self.select(staged,self.expected,self.version)
        self.assertEqual(self.selected,self.old)
        self.assertEqual(hashes(self.old),old_identity)
        intact=self.case/'install-b';shutil.copytree(self.patch,intact)
        with self.assertRaisesRegex(ValueError,'version'):
            self.select(intact,self.expected,'99.0.0')
        self.assertEqual(self.selected,self.old)
        self.assertEqual(hashes(self.old),old_identity)

    def test_stale_pointer_detected_by_candidate_identity_assertion(self):
        # Required negative control: old selected pointer fails candidate identity.
        with self.assertRaises(AssertionError):
            self.assertEqual(hashes(self.selected),self.expected,'stale selected artifact')
        self.select(self.patch,self.expected,self.version)
        self.assertEqual(hashes(self.selected),self.expected)
