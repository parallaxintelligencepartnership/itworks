"""Maintained audit regressions: intended failures are exit-code assertions."""
from support import StateProject


class StateContract(StateProject):
    def must_reject(self):
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('error', result.stdout.lower())

    def test_valid_state_control(self):
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('0 error(s)', result.stdout)

    def test_canonical_critical_control(self):
        self.put('REVIEWS.md', '- [ ] CRITICAL | security-auth | synthetic exposure | Evidence to close: rotate\n')
        self.must_reject()

    def test_indented_critical_must_not_disappear(self):
        self.put('REVIEWS.md', '  - [ ] CRITICAL | security-auth | synthetic exposure | Evidence to close: rotate\n')
        self.must_reject()

    def test_alternate_bullet_critical_must_not_disappear(self):
        self.put('REVIEWS.md', '* [ ] CRITICAL | security-auth | synthetic exposure | Evidence to close: rotate\n')
        self.must_reject()

    def test_empty_acceptance_is_not_a_waiver(self):
        self.put('REVIEWS.md', '- [x] CRITICAL | security-auth | synthetic exposure | Accepted 2026-10-11: see Accepted risks\n### Accepted risks\n')
        self.must_reject()

    def test_profile_requires_complete_enum(self):
        path = self.state / 'PROFILE.md'
        path.write_text(path.read_text().replace('profile: expert', 'profile: expert-invalid'))
        self.must_reject()

    def test_heading_prefix_is_not_required_heading(self):
        path = self.state / 'PROJECT.md'
        path.write_text(path.read_text().replace('## Data\n', '## Database\n'))
        self.must_reject()

    def test_unterminated_bad_finding_control(self):
        self.put('REVIEWS.md', '- [ ] CRITICAL | broken')
        self.must_reject()
