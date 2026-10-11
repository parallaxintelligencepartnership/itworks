"""Frozen historical-template fixtures and real read-only parser compatibility."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from support import REPO, run, tree_snapshot

FIXTURES = REPO / 'tests/fixtures/compatibility'
MANIFEST = json.loads((FIXTURES / 'manifest.json').read_text())


def verify_bytes(test, root, entries):
    for entry in entries:
        data = (root / entry['filename']).read_bytes()
        test.assertEqual(len(data), entry['bytes'], entry['filename'] + ' byte length')
        test.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'], entry['filename'] + ' SHA-256')


class CompatibilityFixtures(unittest.TestCase):
    def test_frozen_hashes(self):
        verify_bytes(self, FIXTURES, MANIFEST['sources'])
        for source in MANIFEST['sources']:
            data = (FIXTURES / source['filename']).read_bytes()
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            self.assertEqual(hashlib.sha1(blob).hexdigest(), source['blob_sha'])
        for case in MANIFEST['cases']:
            with self.subTest(case=case['name']):
                verify_bytes(self, FIXTURES / case['name'], case['files'])
                actual = {p.relative_to(FIXTURES / case['name']).as_posix() for p in (FIXTURES / case['name']).rglob('*') if p.is_file()}
                self.assertEqual(actual, {f['filename'] for f in case['files']})
                self.assertEqual(set(case['expected']), {'check','gate','counts'})

    def test_corruption_is_detected(self):
        case = MANIFEST['cases'][0]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'copy'
            shutil.copytree(FIXTURES / case['name'], target)
            path = target / case['files'][0]['filename']
            data = path.read_bytes()
            path.write_bytes(b'!' + data[1:])
            with self.assertRaisesRegex(AssertionError, 'SHA-256'):
                verify_bytes(self, target, case['files'])

    def test_legacy_categories(self):
        cases = {case['name']:case for case in MANIFEST['cases']}
        for name in ('v1-minimal','v2-missing-map'):
            self.assertEqual(cases[name]['category'], 'additive-drift')
            self.assertEqual(cases[name]['expected']['check']['exit_status'], 0)
        self.assertEqual(cases['v3-corrupt-critical']['category'], 'invalid')
        self.assertEqual(cases['v3-ambiguous-acceptance']['expected']['gate']['exit_status'], 2)

    def test_real_parser_modes_preserve_every_byte(self):
        for case in MANIFEST['cases']:
            with self.subTest(case=case['name']), tempfile.TemporaryDirectory() as temp:
                target = Path(temp) / 'Café project with spaces'
                shutil.copytree(FIXTURES / case['name'], target)
                before = tree_snapshot(target)
                for mode, expected in case['expected'].items():
                    with self.subTest(mode=mode):
                        result = run(['bash', REPO / 'scripts/itworks-state.sh', mode, target])
                        self.assertEqual(result.returncode, expected['exit_status'], result.stdout + result.stderr)
                        records = [line.split('\t') for line in result.stdout.splitlines()]
                        self.assertEqual(records[0], ['FORMAT','1'])
                        self.assertEqual(records[-1][0], 'SUMMARY')
                        ids = {r[1] for r in records if r[0] in ('ERROR','WARN','BLOCKED')}
                        self.assertTrue(set(expected['diagnostic_ids']) <= ids, (expected, ids))
                        if mode == 'counts' and result.returncode == 0:
                            self.assertEqual({r[1]:int(r[2]) for r in records if r[0]=='COUNT'}, case['counts'])
                        if result.returncode:
                            self.assertFalse(any(r[0]=='COUNT' for r in records))
                        if case['name']=='v3-valid':
                            self.assertEqual(records[-1], ['SUMMARY','0','0','0'])
                        self.assertEqual(tree_snapshot(target), before)
                        self.assertNotIn("I accept this specific risk; don't rewrite my words.", result.stdout)
                        self.assertNotIn("CRITICAL delete others' records?? needs checking", result.stdout)

if __name__ == '__main__':
    unittest.main()
