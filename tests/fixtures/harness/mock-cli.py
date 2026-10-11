#!/usr/bin/env python3
"""Offline CLI double. No network/client imports or subprocess/tool execution."""
import json
import os
from pathlib import Path
import sys
import time

config = json.loads(Path(os.environ['ITWORKS_MOCK_CONFIG']).read_text())
if '--version' in sys.argv:
    print('offline-mock-1')
    sys.exit(0)
if '--help' in sys.argv:
    print('offline mock only')
    sys.exit(0)
record = Path(config['record'])
with record.open('a') as out:
    out.write(json.dumps({'cwd':os.getcwd(), 'argv':sys.argv[1:],
        'config_dir':os.environ.get('CLAUDE_CONFIG_DIR'),
        'home':os.environ.get('HOME'),
        'credential_present':bool(os.environ.get('ANTHROPIC_API_KEY'))})+'\n')
time.sleep(config.get('delay',0))
print(config.get('reply','Mock assistant response.'),end='')
print(config.get('stderr',''),end='',file=sys.stderr)
sys.exit(config.get('exit',0))
