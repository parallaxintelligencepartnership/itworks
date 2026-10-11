#!/usr/bin/env python3
"""Validate external candidate evidence; no publish/install action."""
import argparse
import hashlib
import json
from pathlib import Path
import re

REQUIRED = ('identity','unit-macos','unit-linux','integration-macos','integration-linux',
            'parser-regressions','oracle','recovery','installed-local','installed-cache',
            'live-canary','workflow-behavior','performance-macos','performance-linux',
            'release-notes','independent-review','process')


def validate(matrix, evidence_root):
    evidence_root=Path(evidence_root).resolve()
    if matrix.get('schema_version')!=1 or not re.fullmatch(r'[0-9a-f]{40}',matrix.get('candidate','')):
        raise ValueError('unsupported matrix identity')
    cells=matrix.get('cells')
    if not isinstance(cells,list):raise ValueError('missing cells')
    by_id={}
    for cell in cells:
        name=cell.get('id')
        if name not in REQUIRED and name!='approval':raise ValueError('unknown gate cell')
        if name in by_id:raise ValueError('duplicate gate cell: '+name)
        by_id[name]=cell
    missing=set(REQUIRED)-by_id.keys()
    if missing:raise ValueError('missing required cells: '+', '.join(sorted(missing)))
    issues=[]
    for name in REQUIRED:
        cell=by_id[name]
        if cell.get('candidate')!=matrix['candidate']:
            issues.append(name+': candidate mismatch');continue
        status=cell.get('status')
        if status!='PASS':
            issues.append(name+': '+str(status));continue
        checks=cell.get('checks',{})
        if (type(checks.get('passed')) is not int or checks['passed']<1 or
                any(type(checks.get(key)) is not int or checks[key]!=0 for key in ('failed','skipped'))):
            issues.append(name+': missing, failed or skipped checks');continue
        if not all(isinstance(cell.get(key),str) and cell[key].strip() for key in ('command','reviewer','evidence','sha256')):
            issues.append(name+': incomplete evidence metadata');continue
        relative=Path(cell['evidence'])
        if relative.is_absolute() or '..' in relative.parts:
            issues.append(name+': escaping evidence');continue
        path=evidence_root/relative
        if any(part.is_symlink() for part in (path,*path.parents) if part!=evidence_root and evidence_root in part.parents):
            issues.append(name+': linked evidence');continue
        if not path.is_file() or evidence_root not in path.resolve().parents:
            issues.append(name+': missing evidence');continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=cell['sha256']:
            issues.append(name+': evidence hash mismatch')
    if issues:raise ValueError('; '.join(issues))
    return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('matrix');args=parser.parse_args()
    path=Path(args.matrix)
    try:
        validate(json.loads(path.read_text()),path.parent)
    except (ValueError,OSError) as exc:
        print('BLOCKED: '+str(exc));return 1
    print('Ready for explicit release approval; no publication performed.');return 0

if __name__=='__main__': raise SystemExit(main())
