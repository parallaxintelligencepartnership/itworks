"""State parsing contracts; real shell entry points, synthetic state only."""
import unittest
from support import StateProject, REPO, run, tree_snapshot


class ParserRegression(StateProject):
    def test_noncanonical_candidates(self):
        for bullet in ('  -', '\t-', '*', '+'):
            with self.subTest(bullet=bullet):
                self.put('REVIEWS.md', bullet + ' [ ] CRITICAL | testing | missing regression | Evidence to close: run regression\n')
                self.assertEqual(self.lint().returncode, 1)

    def test_duplicate_profile(self):
        with (self.state / 'PROFILE.md').open('a') as f:
            f.write('profile: guided\n')
        self.assertEqual(self.lint().returncode, 1)

    def test_inline_comment_and_closing_hash_headings(self):
        p = self.state / 'PROFILE.md'
        p.write_text(p.read_text().replace('profile: expert', 'profile: guided # tone'))
        p = self.state / 'PROJECT.md'
        p.write_text(p.read_text().replace('## Data\n', '## Data ###  \n'))
        self.assertEqual(self.lint().returncode, 0)

    def test_unknown_explicit_version(self):
        p = self.state / 'PROFILE.md'
        p.write_text(p.read_text().replace('format_version: 3', 'format_version: 99'))
        self.assertEqual(self.lint().returncode, 1)

    def test_diagnostics_do_not_echo_findings(self):
        secret = 'synthetic-sensitive-value-never-print'
        self.put('REVIEWS.md', '- [ ] CRITICAL | broken ' + secret)
        result = self.lint()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(secret, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()

class StateProtocol(StateProject):
    def state_op(self, op):
        before = tree_snapshot(self.root)
        result = run(['/bin/bash', REPO / 'scripts/itworks-state.sh', op, self.root])
        self.assertEqual(tree_snapshot(self.root), before)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], 'FORMAT\t1')
        self.assertRegex(lines[-1], r'^SUMMARY\t\d+\t\d+\t\d+$')
        return result

    def test_empty_counts_and_usage(self):
        result = self.state_op('counts')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(sum(x.startswith('COUNT\t') for x in result.stdout.splitlines()), 5)
        for args in ([], ['bad', self.root], ['check']):
            result = run(['/bin/bash', REPO / 'scripts/itworks-state.sh', *args])
            self.assertEqual(result.returncode, 64)
            self.assertEqual(result.stdout, '')

    def test_pipe_description_and_no_final_newline(self):
        self.put('REVIEWS.md', '- [ ] IMPORTANT | testing | command `a | b` needs test | Evidence to close: run suite')
        self.assertEqual(self.state_op('check').returncode, 0)
        self.assertIn('COUNT\tfound\t1', self.state_op('counts').stdout)

    def test_closure_word_in_description_is_not_fixed(self):
        self.put('REVIEWS.md', '- [x] IMPORTANT | testing | says Closed 2026-10-11 | Evidence to close: run suite\n')
        result = self.state_op('counts')
        self.assertIn('W_CLOSURE_MISSING', result.stdout)
        self.assertIn('COUNT\tfixed\t0', result.stdout)

    def test_crlf_and_unusual_root(self):
        import shutil
        target = self.root.parent / 'back\\slash=é space'
        shutil.copytree(self.root, target)
        self.root = target
        self.state = target / '.itworks'
        for path in self.state.iterdir():
            path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual(self.state_op('check').returncode, 0)

    def test_open_critical_gate_without_ship(self):
        (self.root / 'SHIPPED.md').unlink()
        self.put('REVIEWS.md', '- [ ] CRITICAL | testing | missing test | Evidence to close: run suite\n')
        self.assertEqual(self.state_op('check').returncode, 0)
        self.assertEqual(self.state_op('gate').returncode, 2)
        self.assertEqual(self.state_op('counts').returncode, 0)

class ReviewRegressions(StateProtocol):
    def test_empty_ship_still_blocks_open_critical(self):
        (self.root / 'SHIPPED.md').write_text('')
        self.put('REVIEWS.md', '- [ ] CRITICAL | testing | missing test | Evidence to close: run test\n')
        self.assertEqual(self.state_op('check').returncode, 1)

    def test_embedded_closure_cannot_count_as_fix(self):
        self.put('REVIEWS.md', '- [x] IMPORTANT | testing | command `x | Closed 2026-10-11: demo` is not evidence | Evidence to close: real check\n')
        self.assertIn('COUNT\tfixed\t0', self.state_op('counts').stdout)

    def test_empty_critical_closure_blocks_strict_gate(self):
        self.put('REVIEWS.md', '- [x] CRITICAL | testing | missing test | Closed 2026-10-11:\n')
        self.assertEqual(self.state_op('check').returncode, 0)
        self.assertEqual(self.state_op('gate').returncode, 2)

class CheckedSyntaxReview(StateProtocol):
    def test_indented_checked_critical_blocks_gate(self):
        self.put('REVIEWS.md', '  - [x] CRITICAL | testing | missing test | Closed 2026-10-11: words\n')
        self.assertEqual(self.state_op('gate').returncode, 2)

    def test_malformed_archive_checked_line_blocks_counts(self):
        archive=self.state/'archive'; archive.mkdir()
        (archive/'old.md').write_text('  - [x] IMPORTANT | testing | missing test | Closed 2026-10-11: words\n')
        result=self.state_op('counts')
        self.assertEqual(result.returncode,1)
        self.assertNotIn('COUNT\t',result.stdout)

class DanglingInputs(StateProtocol):
    def test_dangling_archive_is_io_failure(self):
        (self.state/'archive').symlink_to(self.root/'missing-archive')
        result=self.state_op('counts')
        self.assertEqual(result.returncode,1)
        self.assertNotIn('COUNT\t',result.stdout)

    def test_dangling_optional_files_are_not_absent(self):
        for path in (self.state/'MAP.md', self.root/'SHIPPED.md'):
            original=path.read_bytes();path.unlink();path.symlink_to(self.root/'missing')
            self.assertEqual(self.state_op('check').returncode,1)
            path.unlink();path.write_bytes(original)
