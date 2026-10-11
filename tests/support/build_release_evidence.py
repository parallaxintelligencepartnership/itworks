#!/usr/bin/env python3
"""Build exact-commit release evidence outside its source/payload; no publication."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from release_artifacts import extract_archive, hashes, RELEASE

COMMANDS=('project-kickoff','project-resume','project-checkpoint','project-closeout','project-audit')


def validate_artifact(root, version):
    root=Path(root)
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('artifact symlinks are unsupported')
    manifest=json.loads((root/'.claude-plugin/plugin.json').read_text())
    marketplace=json.loads((root/'.claude-plugin/marketplace.json').read_text())
    if not isinstance(manifest,dict) or not isinstance(marketplace,dict):
        raise ValueError('manifest and marketplace must be JSON objects')
    if marketplace.get('name') != 'itworks' or not isinstance(marketplace.get('plugins'),list):
        raise ValueError('marketplace identity mismatch')
    if not all(isinstance(p,dict) for p in marketplace['plugins']):
        raise ValueError('marketplace plugin entry must be an object')
    entries=[p for p in marketplace['plugins'] if p.get('name')=='itworks']
    if len(entries)!=1 or entries[0].get('source')!='./':
        raise ValueError('marketplace plugin identity mismatch')
    if manifest.get('name')!='itworks':
        raise ValueError('plugin name mismatch')
    if manifest.get('version') != version:
        raise ValueError('manifest version mismatch')
    if version == '1.0.0' or not re.fullmatch(r'\d+\.\d+\.\d+',version):
        raise ValueError('changed patch payload requires a unique release version')
    changelog=(root/'CHANGELOG.md').read_text()
    if not re.search(r'^## \['+re.escape(version)+r'\]',changelog,re.M):
        raise ValueError('changelog release version mismatch')
    required=['references/state-format.md','references/publish.md','references/upgrade-recovery.md','scripts/itworks-lint.sh','scripts/itworks-state.sh','scripts/itworks-state.awk','scripts/itworks-recovery.sh','scripts/itworks-test-copy.sh']
    required += ['skills/'+name+'/SKILL.md' for name in COMMANDS]
    required += ['commands/'+name.removeprefix('project-')+'.md' for name in COMMANDS]
    for relative in required:
        if not (root/relative).is_file():
            raise ValueError('missing release payload: '+relative)
    env=os.environ.copy();env.update(ITWORKS_DISABLE='0',CLAUDE_PROJECT_DIR=str(root),CLAUDE_PLUGIN_ROOT=str(root))
    hook=subprocess.run(['/bin/bash',str(root/'hooks/session-start.sh')],cwd=root,env=env,capture_output=True,text=True,timeout=15)
    if hook.returncode or 'itworks v'+version not in hook.stdout:
        raise ValueError('hook identity mismatch or global policy suppressed required evidence')
    return manifest


def build(repo,candidate,base,output,version,results=()):
    repo=Path(repo).resolve();output=Path(output).resolve()
    if output == repo or repo in output.parents:
        raise ValueError('evidence output must be external to source artifact')
    if output.exists():
        raise ValueError('evidence destination already exists')
    def git(*args):
        return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True,timeout=30,env={**os.environ,"GIT_OPTIONAL_LOCKS":"0"}).stdout
    for commit in (candidate,base):
        if not re.fullmatch('[0-9a-f]{40}',commit):
            raise ValueError('full immutable commit SHA required')
        git('cat-file','-e',commit+'^{commit}')
    if git('status','--porcelain=v1','--untracked-files=all').strip():
        raise ValueError('freeze requires a clean candidate repository')
    output.mkdir(parents=True)
    archive=git('archive','--format=tar',candidate)
    (output/'candidate.tar').write_bytes(archive)
    artifact=output/'artifact';extract_archive(archive,artifact)
    manifest=validate_artifact(artifact,version)
    result_evidence=[]
    for specification in results:
        command,separator,path=specification.partition('=')
        if not separator or not command.strip():
            raise ValueError('result must be COMMAND=/absolute/result-file')
        source=Path(path)
        if not source.is_file():
            raise ValueError('missing test result evidence')
        target=output/('result-'+str(len(result_evidence))+source.suffix)
        target.write_bytes(source.read_bytes())
        result_evidence.append({'command':command,'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    identity={'schema_version':1,'candidate':candidate,'base_release':base,'version':manifest['version'],
              'archive_sha256':hashlib.sha256(archive).hexdigest(),'files':hashes(artifact),
              'platform':platform.platform(),'python':sys.version,'shell':subprocess.run(['/bin/bash','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0],
              'test_results':result_evidence,'qualification':'NOT RUN' if not result_evidence else 'Evidence attached; gate matrix independently determines status'}
    (output/'identity.json').write_text(json.dumps(identity,indent=2,sort_keys=True)+'\n')
    (output/'tag-to-candidate.name-status').write_bytes(git('diff','--name-status',base,candidate))
    (output/'tag-to-candidate.diff').write_bytes(git('diff',base,candidate))
    return identity


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',default=os.environ.get('ITWORKS_REPO_ROOT',str(Path(__file__).resolve().parents[2])))
    parser.add_argument('--candidate',required=True);parser.add_argument('--base',default=RELEASE)
    parser.add_argument('--version',default='1.0.1');parser.add_argument('--output',required=True)
    parser.add_argument('--result',action='append',default=[],help='COMMAND=/absolute/result-file (repeatable)')
    args=parser.parse_args()
    identity=build(args.repo,args.candidate,args.base,args.output,args.version,args.result)
    print(json.dumps({key:identity[key] for key in ('candidate','version','archive_sha256')}))

if __name__=='__main__':
    main()
