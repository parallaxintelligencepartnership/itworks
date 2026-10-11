"""Regenerate synthetic states from immutable historical specification templates."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
RELEASE = '0b972ac8232825d82f16023f54d3ccbeda443813'
AUDIT = '7df722830da8fe3a3872459e06308d2d53f4153b'
SOURCE = 'references/state-format.md'
QUOTE = "I accept this specific risk; don't rewrite my words."

def sha(data):
    return hashlib.sha256(data).hexdigest()

def generate():
    sources = []
    for name, commit in [('released', RELEASE), ('audited', AUDIT)]:
        data = subprocess.run(['git', 'show', commit + ':' + SOURCE], check=True, capture_output=True).stdout
        blob = subprocess.run(['git', 'rev-parse', commit + ':' + SOURCE], check=True, capture_output=True, text=True).stdout.strip()
        filename = 'sources/' + name + '-state-format.md'
        (ROOT / filename).write_bytes(data)
        sources.append(dict(commit=commit, source_path=SOURCE, blob_sha=blob, filename=filename, sha256=sha(data), bytes=len(data)))
    source = (ROOT / sources[0]['filename']).read_text()
    templates = {}
    for filename in ['PROJECT.md', 'MAP.md', 'DECISIONS.md', 'REVIEWS.md', 'PROFILE.md']:
        section = source.split('## ' + filename + '\n', 1)[1]
        templates[filename] = re.search(r'```markdown\n(.*?)```', section, re.S).group(1)
    replacements = {'name': 'Café synthetic project', 'YYYY-MM-DD': '2026-10-11', 'n': '1', 'lens-id, lens-id': 'security-auth, testing', 'verbatim': QUOTE, 'finding text': 'API key in client code (public/app.js:1)', 'condition or date': 'next closeout', 'YYYY-MM-DD @<git short sha>, or none before the first checkpoint': '2026-10-11 @7df7228', 'YYYY-MM-DD @<git short sha>, or none': 'none'}
    base = {}
    for filename, value in templates.items():
        for key in sorted(replacements, key=len, reverse=True):
            value = value.replace('<' + key + '>', replacements[key])
        value = re.sub(r'<[^<>]*>', 'synthetic example', value)
        if filename == 'REVIEWS.md':
            value = value.replace('- [ ] CRITICAL', '- [x] CRITICAL').replace('Evidence to close: grep of client dirs and built bundle returns no key patterns', 'Closed 2026-10-11: synthetic check passes')
        base['.itworks/' + filename] = value.encode()
    cases = []
    def add(name, files=None, category='valid', statuses=(0,0,0), diagnostics=None, counts=(3,2,1,0,1), version=3):
        files = dict(base if files is None else files)
        destination = ROOT / name
        destination.mkdir(exist_ok=True)
        manifest_files = []
        for filename, data in sorted(files.items()):
            path = destination / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            manifest_files.append(dict(filename=filename, bytes=len(data), sha256=sha(data)))
        cases.append(dict(name=name, state_version=version, category=category, expected={mode:dict(exit_status=status, diagnostic_ids=(diagnostics or {}).get(mode, [])) for mode,status in zip(('check','gate','counts'), statuses)}, counts=dict(zip(('found','fixed','accepted','critical_open','critical_accepted'), counts)), files=manifest_files))
    add('v3-valid')
    for version in (1,2):
        files = dict(base); del files['.itworks/MAP.md']
        profile = files['.itworks/PROFILE.md'].decode()
        profile = re.sub(r'^last_audit:.*\n', '', profile, flags=re.M)
        ids = ['W_MAP_MISSING','W_AUDIT_MISSING']
        if version == 1:
            profile = re.sub(r'^format_version:.*\n|^  llm-security:.*\n', '', profile, flags=re.M).replace('2026-10-11 @7df7228','2026-10-11')
            ids += ['W_FORMAT_VERSION','W_DEBT_MISSING','W_CHECKPOINT_SHA']
        else:
            profile = profile.replace('format_version: 3','format_version: 2')
        files['.itworks/PROFILE.md'] = profile.encode()
        add('v1-minimal' if version == 1 else 'v2-missing-map', files, 'additive-drift', diagnostics={m:ids for m in ('check','gate','counts')}, version=None if version == 1 else 2)
    line = '- [ ] CRITICAL | testing | synthetic open risk | Evidence to close: run synthetic check'
    for name, value, invalid in [('canonical',line,False),('spaces','  '+line,True),('tab','\t'+line,True),('star','*'+line[1:],True),('unterminated',line,False),('raw',"- [ ] CRITICAL delete others' records?? needs checking",True)]:
        files = dict(base); files['.itworks/REVIEWS.md'] = ('# Reviews\n\n## Checkpoint 1 - 2026-10-11 - lenses: testing\n### Findings\n'+value+('' if name=='unterminated' else '\n')).encode()
        add('v3-corrupt-critical' if name=='raw' else 'v3-critical-'+name,files,'invalid' if invalid else 'open-critical',statuses=(1,1,1) if invalid else (0,2,0),diagnostics={m:['E_FINDING_SYNTAX'] for m in ('check','gate','counts')} if invalid else {'gate':['B_CRITICAL_OPEN']},counts=(1,0,0,1,0))
    for name, field, old, new, code in [('profile-invalid','PROFILE.md','profile: guided','profile: guided-invalid','E_PROFILE_VALUE'),('profile-duplicate','PROFILE.md','profile: guided','profile: expert\nprofile: guided','E_PROFILE_DUPLICATE'),('database','PROJECT.md','## Data\n','## Database\n','E_PROJECT_HEADING')]:
        files=dict(base); key='.itworks/'+field; files[key]=files[key].decode().replace(old,new).encode()
        add('v3-'+name, files,'invalid',statuses=(1,1,1),diagnostics={m:[code] for m in ('check','gate','counts')})
    for name, transform, statuses, diagnostics, category in [
        ('malformed-acceptance',lambda t:t.split('### Accepted risks')[0]+'### Accepted risks\n',(1,1,1),{m:['E_ACCEPTANCE_EMPTY'] for m in ('check','gate','counts')},'invalid'),
        ('ambiguous-acceptance',lambda t:t.replace('| API key in client code (public/app.js:1) | User', '| different historical risk | User'),(0,2,2),{'check':['W_ACCEPTANCE_LINK'],'gate':['B_ACCEPTANCE_LINK'],'counts':['B_ACCEPTANCE_LINK']},'acceptance-review'),
        ('legacy-acceptance',lambda t:t.replace(' | Revisit when: next closeout',''),(0,0,0),{m:['W_REVISIT_MISSING'] for m in ('check','gate','counts')},'additive-drift'),
        ('closed-description',lambda t:t.replace('no failure-path test for login | Closed 2026-10-11: test_login_rejects_bad_password passes','Closed 2026-10-11 appears in prose | Evidence to close: run regression'),(0,0,0),{m:['W_CLOSURE_MISSING'] for m in ('check','gate','counts')},'closure-drift')]:
        files=dict(base); files['.itworks/REVIEWS.md']=transform(files['.itworks/REVIEWS.md'].decode()).encode()
        add('v3-'+name,files,category,statuses,diagnostics,counts=(3,1,1,0,1) if name=='closed-description' else (3,2,1,0,1))
    files=dict(base); files['.itworks/REVIEWS.md']=b'# Reviews\n'; files['.itworks/archive/REVIEWS-2026-10-01-to-2026-10-11.md']=b'# Reviews\n\n## Checkpoint 1 - 2026-10-11 - lenses: testing\n- [x] IMPORTANT | testing | archived synthetic risk | Closed 2026-10-11: synthetic test passes\n'
    add('v3-archive',files,counts=(1,1,0,0,0))
    add('v3-crlf',{k:v.replace(b'\n',b'\r\n') for k,v in base.items()})
    add('v3-no-final-newline',{k:v.rstrip(b'\n') for k,v in base.items()})
    (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,sources=sources,cases=cases),indent=2)+'\n')

if __name__ == '__main__':
    generate()
