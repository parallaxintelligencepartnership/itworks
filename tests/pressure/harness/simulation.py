"""Developer-only deterministic offline simulation mechanics. Live mode fails closed.

Python is not a consumer runtime dependency. The only subprocess target is the
checked-in mock CLI; selecting mock never resolves or invokes claude from PATH.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def relative_input(value, kind):
    path=Path(value)
    if path.is_absolute() or '..' in path.parts or path.parts[0] != kind:
        raise ValueError('prompt input outside approved '+kind+' paths')
    target=ROOT/path
    if target.is_symlink() or not target.resolve().is_relative_to((ROOT/kind).resolve()):
        raise ValueError('symlink/outside prompt input')
    return target

def entries(path):
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith('#')]

def run(case_arg, model, runs):
    if os.environ.get('ITWORKS_HARNESS_MODE') != 'mock':
        raise ValueError('BLOCKED: no approved live adapter')
    if not 1 <= runs <= 10:
        raise ValueError('runs must be 1..10')
    timeout=float(os.environ.get('ITWORKS_TIMEOUT_SECONDS','30'))
    maximum=int(os.environ.get('ITWORKS_MAX_REQUESTS','20'))
    if not 0 < timeout <= 300 or not 1 <= maximum <= 100:
        raise ValueError('timeout must be >0..300 seconds; max requests 1..100')
    case=Path(case_arg)
    if not case.is_dir(): case=HERE/'cases'/case_arg
    case=case.resolve()
    fixture=(case/'fixture.md').read_bytes()
    script=(case/'user-turns.txt').read_bytes()
    turns=[t.strip() for t in re.split(r'^---\s*$',script.decode(),flags=re.M) if t.strip()]
    if not turns or len(turns)>20 or len(turns)*runs>maximum:
        raise ValueError('script exceeds explicit request/turn bound or has no turns')
    inputs={}
    for value in entries(case/'target.txt'):
        path=relative_input(value,'skills')
        if path.name!='SKILL.md':raise ValueError('target must name a SKILL.md')
        inputs[value]=path.read_bytes()
    if not inputs:raise ValueError('target.txt has no skill')
    for value in entries(HERE/'reference-manifest.txt'):
        inputs[value]=relative_input(value,'references').read_bytes()
    inputs['fixture.md']=fixture
    inputs['user-turns.txt']=script
    inputs['target.txt']=(case/'target.txt').read_bytes()
    inputs['reference-manifest.txt']=(HERE/'reference-manifest.txt').read_bytes()
    preamble='Text simulation only. Follow the supplied skill and reference contents. No plugin is activated.\n'
    for name,data in inputs.items():
        if name not in ('user-turns.txt','target.txt','reference-manifest.txt'):
            preamble+='\n===== '+name+' =====\n'+data.decode()+'\n'
    config=json.loads(Path(os.environ['ITWORKS_MOCK_CONFIG']).read_text())
    if not isinstance(config,dict):raise ValueError('mock config must be an object')
    results=Path(os.environ.get('ITWORKS_RESULTS_DIR',str(Path(tempfile.gettempdir())/'itworks-pressure-results'))).resolve()
    if results.is_relative_to(ROOT):raise ValueError('artifacts must be outside checkout')
    results.mkdir(parents=True,exist_ok=True)
    sha=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,timeout=5)
    plugin_sha=sha.stdout.strip() if sha.returncode==0 else 'unknown'
    for number in range(runs):
        artifact=Path(tempfile.mkdtemp(prefix='run-',dir=results))
        os.chmod(artifact,0o700)
        snapshot=artifact/'inputs';snapshot.mkdir(mode=0o700)
        for name,data in inputs.items():
            target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        manifest={'schema_version':1,'status':'INCOMPLETE','mode':'offline-mock',
            'requested_model':model,'resolved_model':'unknown','cli_version':'offline-mock-1',
            'plugin_sha':plugin_sha,'preflight_identity':'mock-only-v1; real host BLOCKED',
            'input_hashes':{name:digest(data) for name,data in inputs.items()},
            'request_limit':maximum,'timeout_seconds':timeout,'turns':[]}
        conversation=[]
        write_json(artifact/'manifest.json',manifest)
        write_json(artifact/'conversation.json',conversation)
        failure=None
        with tempfile.TemporaryDirectory(prefix='itworks-simulation-') as tmp:
            workspace=Path(tmp)
            if workspace.resolve().is_relative_to(ROOT):raise ValueError('temporary cwd must be outside checkout')
            cwd=workspace/'cwd';cwd.mkdir(mode=0o700)
            config_dir=workspace/'config';config_dir.mkdir(mode=0o700)
            mock_config=workspace/'mock.json';write_json(mock_config,config)
            # Explicit environment; never copy settings, auth or credentials. HOME is not changed.
            env={'PATH':os.defpath,'ITWORKS_MOCK_CONFIG':str(mock_config),
                 'CLAUDE_CONFIG_DIR':str(config_dir)}
            if 'HOME' in os.environ:env['HOME']=os.environ['HOME']
            for index,user in enumerate(turns,1):
                conversation.append({'role':'user','content':user})
                prompt=preamble+'\n===== CONVERSATION =====\n'+'\n'.join(t['role'].upper()+': '+t['content'] for t in conversation)
                prompt+='\nReply only with the next assistant turn; never author a user turn.'
                (artifact/f'prompt-{index:03}.txt').write_text(prompt)
                args=['-p',prompt,'--model',model,'--tools','', '--safe-mode',
                      '--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
                      '--setting-sources','','--disable-slash-commands',
                      '--no-session-persistence','--output-format','text']
                # This argv shape is mechanically tested, not advertised as host qualified.
                start=time.monotonic()
                with (artifact/f'stdout-{index:03}.txt').open('wb') as out, (artifact/f'stderr-{index:03}.txt').open('wb') as err:
                    proc=subprocess.Popen([sys.executable,str(ROOT/'tests/fixtures/harness/mock-cli.py')]+args,
                        cwd=cwd,env=env,stdout=out,stderr=err,start_new_session=True)
                    try:status=proc.wait(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid,signal.SIGKILL);proc.wait();status=124
                reply=(artifact/f'stdout-{index:03}.txt').read_text()
                event={'number':index,'prompt_sha256':digest(prompt.encode()),'exit_status':status,
                       'elapsed_seconds':time.monotonic()-start}
                manifest['turns'].append(event)
                if status!=0:failure=f'CLI exit {status}'
                elif not reply.strip():failure='whitespace/empty response'
                else:conversation.append({'role':'assistant','content':reply})
                write_json(artifact/'conversation.json',conversation)
                write_json(artifact/'manifest.json',manifest)
                if failure:break
        manifest['status']='INCOMPLETE' if failure else 'CAPTURED'
        manifest['failure']=failure
        write_json(artifact/'manifest.json',manifest)
        print(str(artifact))
        if failure:
            print('simulation incomplete: '+failure,file=sys.stderr)
            return 1
    return 0

if __name__=='__main__':
    try:
        if len(sys.argv) not in (3,4):raise ValueError('usage: simulation.py case model [runs]')
        sys.exit(run(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)==4 else 1))
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as error:
        print('simulation: '+str(error),file=sys.stderr);sys.exit(1)
