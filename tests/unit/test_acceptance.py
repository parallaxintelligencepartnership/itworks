import unittest
from test_state_parser import StateProtocol


class Acceptance(StateProtocol):
    def accepted(self, description='specific risk'):
        return '- [x] CRITICAL | testing | ' + description + ' | Accepted 2026-10-11: see Accepted risks\n'

    def entry(self, description='specific risk', words='I accept this specific risk; don\'t rewrite my words.'):
        return '- 2026-10-11 | ' + description + ' | User\'s words: "' + words + '"\n'

    def test_exact_unique_legacy_quote_without_revisit(self):
        self.put('REVIEWS.md', self.accepted() + '### Accepted risks\n' + self.entry())
        result = self.state_op('gate')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('W_REVISIT_MISSING', result.stdout)

    def test_mismatch_warns_check_blocks_gate_and_counts(self):
        self.put('REVIEWS.md', self.accepted() + '### Accepted risks\n' + self.entry('another risk'))
        self.assertEqual(self.state_op('check').returncode, 0)
        for op in ('gate', 'counts'):
            result = self.state_op(op)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertNotIn('COUNT\t', result.stdout)

    def test_duplicate_findings_or_entries_are_ambiguous(self):
        for findings, entries in ((2, 1), (1, 2)):
            self.put('REVIEWS.md', self.accepted()*findings + '### Accepted risks\n' + self.entry()*entries)
            self.assertEqual(self.state_op('gate').returncode, 2)

    def test_empty_quote_is_structural(self):
        self.put('REVIEWS.md', self.accepted() + '### Accepted risks\n' + self.entry(words='   '))
        for op in ('check', 'gate', 'counts'):
            self.assertEqual(self.state_op(op).returncode, 1)

    def test_pipe_inside_description_and_quote(self):
        description = 'pipeline `a | b` breaks'
        self.put('REVIEWS.md', self.accepted(description) + '### Accepted risks\n' + self.entry(description, 'keep a | b'))
        self.assertEqual(self.state_op('gate').returncode, 0)

    def test_archive_counts_and_malformed_rejection(self):
        archive = self.state / 'archive'
        archive.mkdir()
        self.put('REVIEWS.md', self.accepted() + '### Accepted risks\n' + self.entry())
        (archive / 'é old.md').write_text('- [x] IMPORTANT | testing | old fix | Closed 2026-10-11: suite passed\n- [x] ADVISORY | testing | old verification | Verified 2026-10-11: suite passed\n')
        result = self.state_op('counts')
        self.assertEqual(result.returncode, 0, result.stdout)
        for key, value in {'found':3,'fixed':2,'accepted':1,'critical_open':0,'critical_accepted':1}.items():
            self.assertIn(f'COUNT\t{key}\t{value}', result.stdout)
        (archive / 'é old.md').write_text('* [ ] CRITICAL | broken\n')
        result = self.state_op('counts')
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('COUNT\t', result.stdout)

    def test_empty_quote_invalid_date_is_still_structural(self):
        self.put('REVIEWS.md', self.accepted()+'### Accepted risks\n- no-date | specific risk | User\'s words: "   "\n')
        self.assertEqual(self.state_op('check').returncode,1)
