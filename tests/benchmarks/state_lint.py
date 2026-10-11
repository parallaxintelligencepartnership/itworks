#!/usr/bin/env python3
"""Comparable read-only lint timing on pinned artifact copies (developer-only)."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import statistics
import shutil
import subprocess
import tempfile
import sys
import time
try:
    import resource
except ImportError:
    resource=None

SIZES=(0,10,100,800,5000)
KEYS=('found','fixed','accepted','critical_open','critical_accepted')

def sha(data):return hashlib.sha256(data).hexdigest()

def files(root):
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}

def write(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def child_usage():
    if resource is None:
        return None,'resource module unavailable'
    try:
        usage=resource.getrusage(resource.RUSAGE_CHILDREN)
        return (usage.ru_utime,usage.ru_stime),None
    except (AttributeError,OSError) as error:
        return None,type(error).__name__

def command(argv,cwd=None,timeout=600):
    before,reason=child_usage()
    start=time.perf_counter_ns()
    result=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=timeout,
        env={**os.environ,'LC_ALL':'C','GIT_OPTIONAL_LOCKS':'0'})
    elapsed=(time.perf_counter_ns()-start)/1_000_000_000
    after,after_reason=child_usage()
    if before is not None and after is not None:
        user=after[0]-before[0];system=after[1]-before[1]
        result.child_cpu={'status':'AVAILABLE','user_seconds':user,
            'system_seconds':system,'total_seconds':user+system}
    else:
        result.child_cpu={'status':'UNAVAILABLE','reason':reason or after_reason}
    return result,elapsed

def make_workload(path,size,distribution,template):
    state=path/'.itworks';state.mkdir(parents=True)
    for name in ('PROJECT.md','PROFILE.md','MAP.md','DECISIONS.md'):
        (state/name).write_bytes((template/name).read_bytes())
    active=size if distribution=='active' else size//5
    lines=[]
    for i in range(size):
        if i<active and i%2==0:
            lines.append(f'- [ ] IMPORTANT | testing | synthetic finding {i} | Evidence to close: regression passes\n')
        else:
            lines.append(f'- [x] IMPORTANT | testing | synthetic finding {i} | Closed 2026-10-11: regression passes\n')
    header='# Reviews\n\n## Checkpoint 1 - 2026-10-11 - lenses: testing\n### Findings\n'
    (state/'REVIEWS.md').write_text(header+''.join(lines[:active]))
    (state/'archive').mkdir()
    if size>active:(state/'archive/REVIEWS-old.md').write_text(header+''.join(lines[active:]))
    return active

def lint(artifact,project):
    result,elapsed=command(['/bin/bash',str(artifact/'scripts/itworks-lint.sh'),str(project)])
    summary=re.search(r'(\d+) error\(s\), (\d+) warning\(s\)',result.stdout)
    return result,elapsed,([int(n) for n in summary.groups()] if summary else None)

def counts(artifact,project):
    helper=artifact/'scripts/itworks-state.sh'
    if helper.exists():
        result,_=command(['/bin/bash',str(helper),'counts',str(project)])
        if result.returncode:raise AssertionError('candidate counts failed: '+result.stdout+result.stderr)
        return {parts[1]:int(parts[2]) for line in result.stdout.splitlines() if (parts:=line.split('\t'))[0]=='COUNT'},'candidate-lifetime'
    publication=(artifact/'references/publish.md').read_text()
    commands=[line for line in publication.splitlines() if re.match(r'^grep -(cE|rhE) ',line)]
    if len(commands) not in (4,5):raise AssertionError('unrecognized historical counts documentation')
    values={}
    for key,script in zip(KEYS,commands):
        result,_=command(['/bin/bash','-c',script],cwd=project)
        # Historical grep -c exits1 for zero matches; record its actual numeric output.
        if result.returncode not in (0,1) or not result.stdout.strip().isdigit():
            raise AssertionError('historical count command failed')
        values[key]=int(result.stdout.strip())
    return values,('released-active-only-four-counts' if len(commands)==4 else 'audited-lifetime')

def summarize(records):
    grouped={}
    for row in records:
        if row['phase']=='measured':grouped.setdefault((row['distribution'],row['size'],row['artifact']),[]).append(row)
    result=[]
    for (distribution,size,artifact),rows in grouped.items():
        values=sorted(row['seconds'] for row in rows)
        available=[row['child_cpu'] for row in rows if row.get('child_cpu',{}).get('status')=='AVAILABLE']
        cpu={'status':'AVAILABLE' if len(available)==len(rows) else 'UNAVAILABLE',
             'available_samples':len(available),'samples':len(rows)}
        if len(available)==len(rows):
            for metric in ('user_seconds','system_seconds','total_seconds'):
                samples=sorted(row[metric] for row in available)
                cpu[metric]={'median':statistics.median(samples),'p95':samples[math.ceil(.95*len(samples))-1],
                    'min':min(samples),'max':max(samples)}
        result.append({'child_cpu':cpu,'distribution':distribution,'size':size,'artifact':artifact,'trials':len(rows),
            'median_seconds':statistics.median(values),'p95_seconds':values[math.ceil(.95*len(values))-1],
            'min_seconds':min(values),'max_seconds':max(values),
            'failures':sum(row['exit_status']!=0 or row['classification'] is None or row['classification'][0]!=0 for row in rows)})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('baseline','baseline-audit','candidate','output'):parser.add_argument('--'+key,required=True,type=Path)
    parser.add_argument('--warmup',type=int,default=5);parser.add_argument('--runs',type=int,default=30)
    args=parser.parse_args()
    if args.warmup<0 or args.runs<1:parser.error('warmup>=0 and runs>=1 required')
    artifacts={key:path.resolve() for key,path in [('released',args.baseline),('audited',args.baseline_audit),('candidate',args.candidate)]}
    output=args.output.resolve()
    if any(output.is_relative_to(path) for path in artifacts.values()):parser.error('output must be outside artifact inputs')
    output.mkdir(parents=True,exist_ok=False)
    identities={name:{'path':str(path),'files':files(path)} for name,path in artifacts.items()}
    bash,_=command(['/bin/bash','--version']);hardware,_=command(['uname','-a'])
    metadata={'schema_version':1,'platform':platform.platform(),'hardware':hardware.stdout.strip(),
        'machine':platform.machine(),'processor':platform.processor(),'cpu_count':os.cpu_count(),
        'bash':bash.stdout.splitlines()[0],'python':platform.python_version(),'warmup':args.warmup,'runs':args.runs,
        'artifact_identities':identities,'sizes':list(SIZES),'distributions':['active','archived'],
        'benchmark_helper_sha256':sha(Path(__file__).read_bytes()),
        'invocation':[sys.executable]+sys.argv,'timer':'time.perf_counter_ns',
        'process_timer':'resource.getrusage(resource.RUSAGE_CHILDREN)',
        'process_timer_availability':bash.child_cpu,
        'template_hashes':files(Path(__file__).resolve().parents[1]/'fixtures/state/v3'),
        'status':'RUNNING','count_comparison_note':'Released publication specifies only four active-file counts; archive/lifetime and fifth metric are not historically equivalent.'}
    toolchain={}
    for tool in ('bash','awk','grep','sed','wc','find','mktemp','rm','dirname','head','tr','od','dd'):
        binary=shutil.which(tool)
        toolchain[tool]={'path':binary,'sha256':sha(Path(binary).read_bytes()) if binary else None}
    metadata['toolchain']=toolchain
    if platform.system()=='Darwin':
        system,_=command(['/usr/sbin/sysctl','-n','machdep.cpu.brand_string','hw.memsize'])
        metadata['cpu_and_memory']=system.stdout.strip()
    write(output/'environment.json',metadata)
    records=[];correctness=[];workloads=[]
    # Workloads retained outside every artifact tree; byte hashes verify read-only execution.
    workload_root=output/'workloads';workload_root.mkdir()
    template=Path(__file__).resolve().parents[1]/'fixtures/state/v3'
    with (output/'trials.jsonl').open('x') as raw:
        for distribution in ('active','archived'):
            for size in SIZES:
                project=workload_root/f'{distribution}-{size}';active=make_workload(project,size,distribution,template)
                identity=files(project)
                workloads.append({'distribution':distribution,'size':size,'active_findings':active,'active_open_important':(active+1)//2,'hashes':identity})
                write(output/'workload-identities.json',workloads)
                for name,artifact in artifacts.items():
                    result,elapsed,classification=lint(artifact,project)
                    values,scope=counts(artifact,project)
                    supported_n=active if scope.startswith('released-') else size
                    expected=dict(zip(KEYS,(supported_n,supported_n-(active+1)//2,0,0,0)))
                    if scope.startswith('released-'):expected.pop('critical_accepted')
                    warning_count=1 if active+4>800 else 0
                    valid=result.returncode==0 and classification==[0,warning_count] and values==expected and files(project)==identity
                    row={'artifact':name,'distribution':distribution,'size':size,'exit_status':result.returncode,
                        'classification':classification,'counts':values,'count_scope':scope,'expected_counts':expected,
                        'valid':valid,'stdout':result.stdout,'stderr':result.stderr}
                    correctness.append(row);write(output/'correctness.json',correctness)
                    if not valid:raise AssertionError('correctness failed before timing: '+json.dumps(row))
                names=list(artifacts)
                for iteration in range(args.warmup+args.runs):
                    order=names[iteration%len(names):]+names[:iteration%len(names)]
                    for name in order:
                        result,elapsed,classification=lint(artifacts[name],project)
                        row={'artifact':name,'distribution':distribution,'size':size,'iteration':iteration,
                            'phase':'warmup' if iteration<args.warmup else 'measured','seconds':elapsed,'elapsed_ns':round(elapsed*1_000_000_000),
                            'exit_status':result.returncode,'classification':classification,'child_cpu':result.child_cpu,
                            'stdout':result.stdout,'stderr':result.stderr}
                        records.append(row);raw.write(json.dumps(row,sort_keys=True)+'\n');raw.flush();os.fsync(raw.fileno())
                        if result.returncode or classification!=[0,warning_count]:raise AssertionError('timed classification changed')
                    write(output/'summary.json',summarize(records))
                if files(project)!=identity:raise AssertionError('workload changed')
                print(f'{distribution} {size}: {args.runs} trials/artifact complete',flush=True)
    if any(files(path)!=identities[name]['files'] for name,path in artifacts.items()):raise AssertionError('artifact changed')
    metadata['status']='COMPLETE';write(output/'environment.json',metadata)
    write(output/'summary.json',summarize(records))

if __name__=='__main__':main()
