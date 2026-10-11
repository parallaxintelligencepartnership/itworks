"""Trusted local Git artifacts; never checkout/reset the caller's repository.

Working-tree mode is development-only. ITWORKS_CANDIDATE_SHA pins qualification
and materializes *only* that exact commit, including no working-tree overlay.
"""
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

REPO = Path(os.environ.get('ITWORKS_REPO_ROOT', Path(__file__).resolve().parents[2])).resolve()
RELEASE = '0b972ac8232825d82f16023f54d3ccbeda443813'
AUDIT = '7df722830da8fe3a3872459e06308d2d53f4153b'


def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args], check=True, capture_output=True, timeout=30, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}).stdout


def extract_archive(data, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        members = archive.getmembers()
        # Validate all before extracting any. Repository package needs regular
        # files/directories only; reject links, device entries and traversal.
        names = set()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] == '.git':
                raise ValueError('unsafe archive path')
            if not (member.isfile() or member.isdir()) or member.name in names:
                raise ValueError('unsupported or duplicate archive member')
            names.add(member.name)
        for member in members:
            path = destination.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, path.open('xb') as output:
                    shutil.copyfileobj(source, output)
                path.chmod(member.mode & 0o777)


def materialize(commit, destination):
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('full immutable commit SHA required')
    git('cat-file', '-e', commit + '^{commit}')  # Missing history is setup error.
    archive = git('archive', '--format=tar', commit)
    extract_archive(archive, destination)
    return {'mode': 'immutable-commit', 'commit': commit, 'archive_sha256': hashlib.sha256(archive).hexdigest()}


def candidate(destination):
    commit = os.environ.get('ITWORKS_CANDIDATE_SHA')
    if commit:
        return materialize(commit, destination)
    head = git('rev-parse', 'HEAD').decode().strip()
    identity = materialize(head, destination)
    paths = git('ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0')
    for raw in paths:
        if not raw:
            continue
        relative = Path(os.fsdecode(raw))
        source = REPO / relative
        target = Path(destination) / relative
        if source.is_symlink():
            raise ValueError('development candidate does not follow symlinks')
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.is_file():
            target.unlink()  # tracked worktree deletion
    identity['mode'] = 'development-working-tree-NOT-release-qualification'
    identity['files'] = hashes(destination)
    return identity


def hashes(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}
