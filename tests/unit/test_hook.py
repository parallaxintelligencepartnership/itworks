"""Hook branches on a temporary script copy; caller HOME is never redefined."""
from pathlib import Path
import tempfile
import unittest
from support import REPO, build_state, run, tree_snapshot


class Hook(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='itworks-hook-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.project = self.root / 'project with spaces'
        self.project.mkdir()
        self.global_marker = self.root / 'global disabled'
        # Replace only the global-marker operand so personal opt-outs cannot
        # affect controls. This is path isolation, not installed-host evidence.
        source = (REPO / 'hooks/session-start.sh').read_text()
        operand = '$HOME/.config/itworks/disabled'
        self.assertEqual(source.count(operand), 1)
        source = source.replace(operand, '${ITWORKS_TEST_GLOBAL_MARKER}')
        hookdir = self.root / 'plugin/hooks'
        hookdir.mkdir(parents=True)
        self.hook = hookdir / 'session-start.sh'
        self.hook.write_text(source)
        manifestdir = hookdir.parent / '.claude-plugin'
        manifestdir.mkdir()
        (manifestdir / 'plugin.json').write_bytes((REPO / '.claude-plugin/plugin.json').read_bytes())

    def invoke(self, disable='0'):
        before = tree_snapshot(self.root)
        result = run(['/bin/bash', self.hook], cwd=self.project, env={
            'CLAUDE_PROJECT_DIR': str(self.project), 'ITWORKS_DISABLE': disable,
            'ITWORKS_TEST_GLOBAL_MARKER': str(self.global_marker)})
        self.assertEqual(tree_snapshot(self.root), before)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_no_state(self):
        self.assertIn('project-kickoff', self.invoke())
        self.assertNotIn('project-resume skill', self.invoke())

    def test_state_and_path_spaces(self):
        build_state(self.project)
        self.assertIn('project-resume skill', self.invoke())

    def test_environment_disable(self):
        build_state(self.project)
        self.assertEqual(self.invoke('1'), '')

    def test_project_disable(self):
        (self.project / '.itworks-off').touch()
        self.assertEqual(self.invoke(), '')

    def test_global_disable(self):
        self.global_marker.touch()
        self.assertEqual(self.invoke(), '')
