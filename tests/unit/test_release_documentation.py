"""Mechanical identity/link checks only; human review assesses claims."""
import json
from pathlib import Path
import re
import unittest
from support import REPO


class ReleaseDocumentation(unittest.TestCase):
    def test_actual_patch_version(self):
        version=json.loads((REPO/'.claude-plugin/plugin.json').read_text())['version']
        self.assertEqual(version,'1.1.0')
        note=REPO/f'docs/releases/{version}.md'
        self.assertTrue(note.is_file())
        self.assertIn(version,note.read_text().splitlines()[0])
        self.assertIn(f'## [{version}]',(REPO/'CHANGELOG.md').read_text())

    def test_candidate_note_identity_and_local_links(self):
        note=REPO/'docs/releases/1.0.1.md'
        self.assertTrue(note.is_file())
        self.assertIn('1.0.1',note.read_text().splitlines()[0])
        self.assertIn('## [1.0.1]',(REPO/'CHANGELOG.md').read_text())
        for filename in ('docs/releases/1.0.1.md','docs/release-checklist.md'):
            path=REPO/filename
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' not in target:
                    self.assertTrue((path.parent/target.split('#')[0]).exists(),target)
