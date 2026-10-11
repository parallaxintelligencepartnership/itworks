#!/usr/bin/env python3
"""Export conversation only with nominal identity removed; never assign a PASS."""
import json
from pathlib import Path
import re
import sys


def export(source, destination):
    manifest=json.loads((source/'manifest.json').read_text())
    conversation=json.loads((source/'conversation.json').read_text())
    identity=manifest['requested_model']
    text='\n\n'.join(turn['role'].upper()+':\n'+turn['content'] for turn in conversation)+'\n'
    if identity:text=re.sub(re.escape(identity),'[model identity removed]',text,flags=re.I)
    destination.mkdir(mode=0o700) # Never overwrite a previous judgment/export.
    (destination/'transcript.txt').write_text(text)
    score={'verdict':'INCONCLUSIVE' if manifest['status']=='CAPTURED' else 'INVALID_EVAL',
           'reviewer':None,'checks':[], 'notes':'Independent judgment required. Captured is not PASS.',
           'allowed_verdicts':['PASS','FAIL','INCONCLUSIVE','INVALID_EVAL']}
    (destination/'score.json').write_text(json.dumps(score,indent=2)+'\n')

if __name__=='__main__':
    try:
        if len(sys.argv)!=3:raise ValueError('usage: export-judge.py raw-run-dir new-judge-dir')
        export(Path(sys.argv[1]),Path(sys.argv[2]))
    except (OSError,ValueError,KeyError) as error:
        print('export: '+str(error),file=sys.stderr);sys.exit(1)
