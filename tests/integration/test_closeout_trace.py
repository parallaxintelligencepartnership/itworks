"""Execute prescribed state/gate operations; not an agent adherence claim."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
from support import StateProject, REPO, run, tree_snapshot


class CloseoutTrace(StateProject):
    def test_new_real_data_finding_before_reckoning_blocks_ship(self):
        (self.root/'SHIPPED.md').unlink()
        # Applicability observation supplied by a synthetic actual store fixture.
        store=self.root/'records.json'; store.write_text('[{"owner":"another person"}]')
        self.assertTrue(json.loads(store.read_text()))
        finding='real user records have no backup'
        self.put('REVIEWS.md','- [ ] CRITICAL | real-data | '+finding+' | Evidence to close: restore backup\n')
        before=tree_snapshot(self.root)
        gate=run(['/bin/bash',REPO/'scripts/itworks-state.sh','gate',self.root])
        self.assertEqual(gate.returncode,2)
        self.assertEqual(tree_snapshot(self.root),before)
        self.assertFalse((self.root/'SHIPPED.md').exists())
        # The test supplies a synthetic explicit per-finding decision; no claim
        # this proves a real user spoke or a host performed the reckoning.
        self.put('REVIEWS.md','- [x] CRITICAL | real-data | '+finding+' | Accepted 2026-10-11: see Accepted risks\n### Accepted risks\n- 2026-10-11 | '+finding+' | User\'s words: "I accept this specific risk" | Revisit when: next closeout\n')
        gate=run(['/bin/bash',REPO/'scripts/itworks-state.sh','gate',self.root])
        self.assertEqual(gate.returncode,0,gate.stdout)

    def test_partial_audit_record_preserves_completion_marker(self):
        profile=(self.state/'PROFILE.md').read_bytes()
        with (self.state/'REVIEWS.md').open('a') as stream:
            stream.write('\n## Audit - 2026-10-11 - INCOMPLETE\nScope: lane a read; lane b unread.\n### Coverage gaps\nLane b remains to read and verify.\n')
        result=self.lint()
        self.assertEqual(result.returncode,0,result.stdout)
        self.assertEqual((self.state/'PROFILE.md').read_bytes(),profile)

    def test_late_critical_requires_another_gate(self):
        (self.root/'SHIPPED.md').unlink()
        cmd=['/bin/bash',REPO/'scripts/itworks-state.sh','gate',self.root]
        self.assertEqual(run(cmd).returncode,0)
        self.put('REVIEWS.md','- [ ] CRITICAL | testing | late failed check | Evidence to close: run regression\n')
        self.assertEqual(run(cmd).returncode,2)
        self.assertFalse((self.root/'SHIPPED.md').exists())

class CommittedLockfiles(unittest.TestCase):
    def test_exact_documented_check_matches_manifest(self):
        import tempfile
        import re
        text=(REPO/'references/dependency-vetting.md').read_text()
        block=text.split('<!-- executable: committed-lock -->')[1].split('<!-- /executable: committed-lock -->')[0]
        script=re.search(r'```bash\n(.*?)```',block,re.S).group(1)
        # Resolve expectations from the actual shared table, not a second policy.
        mapping={}
        for manifest in ('Cargo.toml','composer.json'):
            row=next(line for line in text.splitlines() if line.startswith('| '+manifest+' |'))
            mapping[manifest]=row.split('|')[2].strip().split()[0]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for cmd in (['git','init','-q'],['git','config','user.email','fixture@example.invalid'],['git','config','user.name','Fixture']):
                self.assertEqual(run(cmd,cwd=root).returncode,0)
            (root/'Cargo.toml').write_text('[package]\nname="fixture"\n')
            (root/'Cargo.lock').write_text('# synthetic lock\n')
            (root/'composer.json').write_text('{}\n')
            (root/'package-lock.json').write_text('{}\n')
            self.assertEqual(run(['git','add','--','.'],cwd=root).returncode,0)
            self.assertEqual(run(['git','commit','-qm','fixture'],cwd=root).returncode,0)
            for manifest,want in (('Cargo.toml',0),('composer.json',1)):
                result=run(['/bin/bash','-c',script],cwd=root,env={'lock_path':mapping[manifest]})
                self.assertEqual(result.returncode==0,want==0,result.stderr)
            (root/'composer.lock').write_text('{}\n')
            run(['git','add','--','composer.lock'],cwd=root)
            self.assertNotEqual(run(['/bin/bash','-c',script],cwd=root,env={'lock_path':mapping['composer.json']}).returncode,0)
            run(['git','commit','-qm','lock'],cwd=root)
            self.assertEqual(run(['/bin/bash','-c',script],cwd=root,env={'lock_path':mapping['composer.json']}).returncode,0)
