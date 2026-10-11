"""Offline developer helpers. Synthetic fixtures are not historical artifacts."""
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]


def isolated_git_environment(source):
    """Only this developer test process/children; never edit caller config files."""
    clean={key:value for key,value in source.items() if not key.startswith('GIT_')}
    clean.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                 GIT_CONFIG_SYSTEM=os.devnull, GIT_TERMINAL_PROMPT='0',
                 GIT_OPTIONAL_LOCKS='0', GIT_CONFIG_COUNT='3',
                 GIT_CONFIG_KEY_0='core.hooksPath', GIT_CONFIG_VALUE_0=os.devnull,
                 GIT_CONFIG_KEY_1='commit.gpgsign', GIT_CONFIG_VALUE_1='false',
                 GIT_CONFIG_KEY_2='tag.gpgsign', GIT_CONFIG_VALUE_2='false')
    return clean


# Direct subprocess calls in test modules inherit the same isolation. The parent
# shell environment, HOME and actual global/system Git files remain unchanged.
_test_environment=isolated_git_environment(os.environ)
for _key in list(os.environ):
    if _key.startswith('GIT_'): del os.environ[_key]
os.environ.update({key:value for key,value in _test_environment.items() if key.startswith('GIT_')})


def run(args, *, cwd=None, env=None, timeout=15):
    """Bound subprocesses; timeouts remain infrastructure errors, never RED."""
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    process_env=isolated_git_environment(process_env)
    return subprocess.run([str(a) for a in args], cwd=cwd, env=process_env,
                          text=True, capture_output=True, timeout=timeout)


def tree_snapshot(root):
    """Relative paths, types/modes and byte hashes; do not follow symlinks."""
    root = Path(root)
    result = {}
    for path in sorted(root.rglob('*')):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            content = os.readlink(path).encode()
        elif stat.S_ISREG(mode):
            content = path.read_bytes()
        else:
            content = b''
        result[path.relative_to(root).as_posix()] = (
            stat.S_IFMT(mode), stat.S_IMODE(mode), hashlib.sha256(content).hexdigest())
    return result


def git_snapshot(root):
    """Capture HEAD, raw index digest, porcelain status and all tree bytes."""
    root = Path(root)
    def git(*args):
        output = run(['git', '-c', 'core.fsmonitor=false', '-C', root, *args], env={'GIT_OPTIONAL_LOCKS': '0'})
        if output.returncode:
            raise RuntimeError(output.stderr)
        return output.stdout
    index_path = Path(git('rev-parse', '--git-path', 'index').strip())
    if not index_path.is_absolute():
        index_path = root / index_path
    return {'head': git('rev-parse', 'HEAD').strip(),
            'index': hashlib.sha256(index_path.read_bytes()).hexdigest() if index_path.exists() else None,
            'status': git('status', '--porcelain=v1', '-z', '--untracked-files=all'),
            'tree': tree_snapshot(root)}


def build_state(root, *, version=3, shipped=True):
    """Materialize synthetic format controls. Use U01 artifacts for history claims."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    state = root / '.itworks'
    state.mkdir(exist_ok=True)
    fixture = REPO / 'tests/fixtures/state' / ('v' + str(version))
    for path in fixture.iterdir():
        if path.is_file():
            (state / path.name).write_bytes(path.read_bytes())
    if shipped:
        (root / 'SHIPPED.md').write_text('## Known limitations and accepted risks\n')
    return state


class StateProject(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='itworks-state-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'project with spaces'
        self.state = build_state(self.root)

    def put(self, name, value):
        (self.state / name).write_text(value)

    def lint(self):
        before = tree_snapshot(self.root)
        result = run(['/bin/bash', REPO / 'scripts/itworks-lint.sh', self.root])
        self.assertEqual(tree_snapshot(self.root), before, 'lint modified input state')
        return result
