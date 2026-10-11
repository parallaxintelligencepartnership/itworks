"""Mechanical release identity, no installed plugin mutation."""
import json
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from support import REPO
sys.path.insert(0,str(REPO/'tests/support'))
from build_release_evidence import validate_artifact, build


class ReleaseIdentity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'artifact';self.root.mkdir()
        for name in ('.claude-plugin','hooks','scripts','references','skills','commands'):
            shutil.copytree(REPO/name,self.root/name)
        shutil.copy2(REPO/'CHANGELOG.md',self.root/'CHANGELOG.md')
        manifest=self.root/'.claude-plugin/plugin.json'
        data=json.loads(manifest.read_text());data['version']='1.0.1';manifest.write_text(json.dumps(data,indent=2)+'\n')
        changelog=self.root/'CHANGELOG.md'
        if '## [1.0.1]' not in changelog.read_text():
            changelog.write_text('## [1.0.1] - synthetic test candidate\n\n'+changelog.read_text())

    def test_consistent_identity(self):
        self.assertEqual(validate_artifact(self.root,'1.0.1')['version'],'1.0.1')

    def test_unchanged_version_rejected(self):
        with self.assertRaisesRegex(ValueError,'unique release version'):
            path=self.root/'.claude-plugin/plugin.json';data=json.loads(path.read_text());data['version']='1.0.0';path.write_text(json.dumps(data))
            validate_artifact(self.root,'1.0.0')

    def test_mismatch_and_malformed_manifest(self):
        with self.assertRaisesRegex(ValueError,'manifest version mismatch'):
            validate_artifact(self.root,'1.0.2')
        (self.root/'.claude-plugin/plugin.json').write_text('{broken')
        with self.assertRaises(json.JSONDecodeError):validate_artifact(self.root,'1.0.1')

    def test_changelog_missing_command_and_wrong_hook_rejected(self):
        path=self.root/'CHANGELOG.md';original=path.read_bytes();path.write_text('# No release')
        with self.assertRaisesRegex(ValueError,'changelog'):validate_artifact(self.root,'1.0.1')
        path.write_bytes(original)
        command=self.root/'skills/project-resume/SKILL.md';original=command.read_bytes();command.unlink()
        with self.assertRaisesRegex(ValueError,'missing release payload'):validate_artifact(self.root,'1.0.1')
        command.write_bytes(original)
        (self.root/'hooks/session-start.sh').write_text('echo "itworks v0.0.0"\n')
        with self.assertRaisesRegex(ValueError,'hook identity'):validate_artifact(self.root,'1.0.1')

    def test_escaping_link_rejected(self):
        (self.root/'escape').symlink_to('/tmp')
        with self.assertRaisesRegex(ValueError,'symlink'):validate_artifact(self.root,'1.0.1')

    def test_exact_commit_builder_and_dirty_freeze_rejection(self):
        def git(*args):
            return subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True,text=True).stdout.strip()
        git('init','-q');git('add','.')
        git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','synthetic immutable candidate')
        commit=git('rev-parse','HEAD')
        output=Path(self.temp.name)/'external-evidence'
        identity=build(self.root,commit,commit,output,'1.0.1')
        self.assertEqual(identity['candidate'],commit)
        self.assertEqual(identity['qualification'],'NOT RUN')
        self.assertTrue((output/'candidate.tar').is_file())
        self.assertEqual(json.loads((output/'identity.json').read_text())['files'],identity['files'])
        (self.root/'untracked-note').write_text('preserve me')
        with self.assertRaisesRegex(ValueError,'clean candidate'):
            build(self.root,commit,commit,Path(self.temp.name)/'second','1.0.1')
        with self.assertRaisesRegex(ValueError,'external'):
            build(self.root,commit,commit,self.root/'inside','1.0.1')

    def test_missing_entry_point_wrapper_rejected(self):
        (self.root/'commands/resume.md').unlink()
        with self.assertRaisesRegex(ValueError,'missing release payload'):
            validate_artifact(self.root,'1.0.1')

    def test_malformed_marketplace_rejected(self):
        (self.root/'.claude-plugin/marketplace.json').write_text('{broken')
        with self.assertRaises(json.JSONDecodeError):
            validate_artifact(self.root,'1.0.1')

    def test_required_support_helpers_cannot_be_missing(self):
        for name in ('itworks-recovery.sh','itworks-test-copy.sh'):
            path=self.root/'scripts'/name;original=path.read_bytes();path.unlink()
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'missing release payload'):
                validate_artifact(self.root,'1.0.1')
            path.write_bytes(original)
