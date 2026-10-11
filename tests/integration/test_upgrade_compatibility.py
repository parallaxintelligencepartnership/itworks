"""Actual old → candidate → old artifacts. No installed-host claim."""
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'unit'))
from support import run, tree_snapshot
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'support'))
from release_artifacts import REPO, RELEASE, AUDIT, materialize, candidate, extract_archive

FIXTURES = REPO / 'tests/fixtures/compatibility'
MANIFEST = json.loads((FIXTURES / 'manifest.json').read_text())
OBSERVATIONS = json.loads((FIXTURES / 'historical-results.json').read_text())
COMMANDS = ('project-kickoff','project-resume','project-checkpoint','project-closeout','project-audit')


class UpgradeCompatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='itworks-upgrade-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = Path(cls.temp.name)
        cls.artifacts = {}
        for commit in (RELEASE,AUDIT):
            artifact = cls.directory / commit
            materialize(commit, artifact)
            cls.artifacts[commit] = artifact
        cls.patch = cls.directory / 'candidate'
        cls.identity = candidate(cls.patch)

    def test_old_candidate_old_all_frozen_cases(self):
        for case in MANIFEST['cases']:
            with self.subTest(case=case['name']), tempfile.TemporaryDirectory() as temp:
                project = Path(temp) / 'Café project with spaces'
                shutil.copytree(FIXTURES / case['name'], project)
                before = tree_snapshot(project)
                first = {}
                for commit, artifact in self.artifacts.items():
                    result = run(['bash', artifact / 'scripts/itworks-lint.sh', project])
                    first[commit] = (result.returncode,result.stdout,result.stderr)
                    observed = dict(status=result.returncode,stdout=result.stdout.replace(str(project),'<PROJECT>'),stderr=result.stderr.replace(str(project),'<PROJECT>'))
                    self.assertEqual(observed, OBSERVATIONS[commit][case['name']])
                patch_results=[]
                for _ in range(2):
                    result=run(['bash', self.patch / 'scripts/itworks-lint.sh', project])
                    self.assertEqual(result.returncode,case['expected']['check']['exit_status'],result.stdout+result.stderr)
                    patch_results.append((result.returncode,result.stdout,result.stderr))
                self.assertEqual(*patch_results)
                for mode in ('gate','counts'):
                    result=run(['bash', self.patch/'scripts/itworks-state.sh',mode,project])
                    self.assertEqual(result.returncode,case['expected'][mode]['exit_status'],result.stdout+result.stderr)
                    if result.returncode:
                        self.assertNotIn('COUNT\t',result.stdout)
                for commit,artifact in self.artifacts.items():
                    result=run(['bash',artifact/'scripts/itworks-lint.sh',project])
                    self.assertEqual((result.returncode,result.stdout,result.stderr),first[commit])
                self.assertEqual(tree_snapshot(project),before)

    def test_actual_audit_artifact_demonstrates_expected_red(self):
        project=FIXTURES/'v3-critical-spaces'
        result=run(['bash', self.artifacts[AUDIT]/'scripts/itworks-lint.sh',project])
        self.assertEqual(result.returncode,0,'historical false pass changed unexpectedly')
        with self.assertRaises(AssertionError):
            self.assertEqual(result.returncode,1,'candidate must reject malformed critical')
        patched=run(['bash',self.patch/'scripts/itworks-lint.sh',project])
        self.assertEqual(patched.returncode,1)

    def test_artifact_hooks_and_five_commands(self):
        for artifact in [*self.artifacts.values(),self.patch]:
            with self.subTest(artifact=artifact.name), tempfile.TemporaryDirectory() as temp:
                project=Path(temp)/'project'; shutil.copytree(FIXTURES/'v3-valid',project)
                before=tree_snapshot(project)
                version=json.loads((artifact/'.claude-plugin/plugin.json').read_text())['version']
                for command in COMMANDS:
                    self.assertTrue((artifact/'skills'/command/'SKILL.md').is_file())
                    self.assertTrue((artifact/'commands'/(command.removeprefix('project-')+'.md')).is_file())
                env={'CLAUDE_PROJECT_DIR':str(project),'CLAUDE_PLUGIN_ROOT':str(artifact),'ITWORKS_DISABLE':'1'}
                disabled=run(['bash',artifact/'hooks/session-start.sh'],cwd=project,env=env)
                self.assertEqual((disabled.returncode,disabled.stdout),(0,''))
                # Actual artifact, actual global policy. If user globally disabled
                # it, assert silence instead of overriding that global policy.
                env['ITWORKS_DISABLE']='0'
                enabled=run(['bash',artifact/'hooks/session-start.sh'],cwd=project,env=env)
                self.assertEqual(enabled.returncode,0)
                if (Path.home()/'.config/itworks/disabled').exists():
                    self.assertEqual(enabled.stdout,'')
                else:
                    self.assertIn('itworks v'+version,enabled.stdout)
                    self.assertIn('project-resume',enabled.stdout)
                self.assertEqual(tree_snapshot(project),before)
                (project/'.itworks-off').touch()
                disabled=run(['bash',artifact/'hooks/session-start.sh'],cwd=project,env=env)
                self.assertEqual((disabled.returncode,disabled.stdout),(0,''))

    def test_archive_traversal_and_links_rejected(self):
        for name,link in [('../escape',False),('/absolute',False),('escape',True)]:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as temp:
                data=io.BytesIO()
                with tarfile.open(fileobj=data,mode='w') as archive:
                    entry=tarfile.TarInfo(name)
                    if link:
                        entry.type=tarfile.SYMTYPE;entry.linkname='../escape'
                    archive.addfile(entry)
                with self.assertRaises(ValueError):
                    extract_archive(data.getvalue(),Path(temp)/'artifact')
                self.assertFalse((Path(temp)/'escape').exists())

    def test_documented_normalized_v3_is_old_readable(self):
        # A resulting shape, not a claim that an agent performed a repair.
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/'external-original'
            shutil.copytree(FIXTURES/'v1-minimal',original)
            retained=tree_snapshot(original)
            stage=Path(temp)/'normalized'
            shutil.copytree(original,stage)
            shutil.copy2(FIXTURES/'v3-valid/.itworks/PROFILE.md',stage/'.itworks/PROFILE.md')
            shutil.copy2(FIXTURES/'v3-valid/.itworks/MAP.md',stage/'.itworks/MAP.md')
            reviews=(stage/'.itworks/REVIEWS.md').read_bytes()
            self.assertEqual(reviews,(original/'.itworks/REVIEWS.md').read_bytes())
            for artifact in [*self.artifacts.values(),self.patch]:
                result=run(['bash',artifact/'scripts/itworks-lint.sh',stage])
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(tree_snapshot(original),retained)
