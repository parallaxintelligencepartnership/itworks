#!/usr/bin/env python3
"""Regenerate case8's current lint record from its exact embedded state bytes."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[3]
FIXTURE=ROOT/'tests/pressure/harness/cases/case-8/fixture.md'

def regenerate(write=False):
    source=FIXTURE.read_text()
    with tempfile.TemporaryDirectory(prefix='itworks-case8-') as tmp:
        state=Path(tmp)/'.itworks';state.mkdir()
        for name in ('PROFILE.md','PROJECT.md','DECISIONS.md','REVIEWS.md'):
            pattern=r'## `\.itworks/'+re.escape(name)+r'`[^\n]*\n\n```markdown\n(.*?)```'
            match=re.search(pattern,source,re.S)
            if not match:raise ValueError('missing embedded state '+name)
            (state/name).write_text(match.group(1))
        result=subprocess.run(['/bin/bash',str(ROOT/'scripts/itworks-lint.sh'),tmp],
            capture_output=True,text=True,timeout=15)
        if result.returncode!=1 or 'error(s)' not in result.stdout:
            raise ValueError('unexpected validator setup/result; cannot generate oracle')
    pattern=r'(\$ bash <plugin-root>/scripts/itworks-lint.sh /Users/sam/projects/bookclub\n)(.*?)(\$ echo \$\?\n)\d+\n'
    record=re.search(pattern,source,re.S)
    if not record:raise ValueError('missing lint record')
    replacement=record.group(1)+result.stdout+record.group(3)+str(result.returncode)+'\n'
    corrected=source[:record.start()]+replacement+source[record.end():]
    if write:FIXTURE.write_text(corrected)
    elif corrected!=source:raise ValueError('case8 recorded lint output differs from executed candidate')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true');args=parser.parse_args()
    try:regenerate(args.write)
    except (ValueError,OSError,subprocess.SubprocessError) as error:parser.exit(1,str(error)+'\n')
