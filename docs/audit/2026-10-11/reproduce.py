#!/usr/bin/env python3
"""Audit regressions: desired behavior, deliberately RED on audited 7df7228.

Run: python3 docs/audit/2026-10-11/reproduce.py
Uses temporary synthetic projects, no paid models or network. Product files unchanged.
"""
import datetime
import re
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]


class StateContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="itworks-audit-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / ".itworks"
        self.state.mkdir()
        self.put("PROJECT.md", "\n".join("## " + h for h in (
            "What it is", "Who uses it", "Terminology map", "Stack", "Data",
            "Where it will live", "Definition of done", "Verification expectations")) + "\n")
        self.put("DECISIONS.md", "# Decisions\n")
        self.put("MAP.md", "\n".join("## " + h for h in (
            "Run", "Test", "Layout", "Environment", "Gotchas")) + "\n")
        self.put("PROFILE.md", "format_version: 3\nprofile: expert\n"
                 "last_checkpoint: 2026-10-11 @7df7228\nlast_audit: 2026-10-11 @7df7228\n"
                 "lens_debt:\n  security-auth: 0\n  llm-security: 0\n"
                 "  real-data: 0\n  testing: 0\n  production-readiness: 0\n")
        self.put("REVIEWS.md", "# Reviews\n")
        (self.root / "SHIPPED.md").write_text("## Known limitations and accepted risks\n")

    def put(self, name, value):
        (self.state / name).write_text(value)

    def lint(self):
        return subprocess.run(["bash", str(REPO / "scripts/itworks-lint.sh"), str(self.root)],
                              text=True, capture_output=True, timeout=15)

    def must_reject(self):
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_valid_state_control(self):
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_canonical_critical_control(self):
        self.put("REVIEWS.md", "- [ ] CRITICAL | security-auth | exposed key | Evidence to close: rotate\n")
        self.must_reject()

    def test_indented_critical_must_not_disappear(self):
        self.put("REVIEWS.md", "  - [ ] CRITICAL | security-auth | exposed key | Evidence to close: rotate\n")
        self.must_reject()

    def test_alternate_bullet_critical_must_not_disappear(self):
        self.put("REVIEWS.md", "* [ ] CRITICAL | security-auth | exposed key | Evidence to close: rotate\n")
        self.must_reject()

    def test_empty_acceptance_is_not_a_waiver(self):
        self.put("REVIEWS.md", "- [x] CRITICAL | security-auth | exposed key | Accepted 2026-10-11: see Accepted risks\n### Accepted risks\n")
        self.must_reject()

    def test_profile_requires_complete_enum(self):
        path = self.state / "PROFILE.md"
        path.write_text(path.read_text().replace("profile: expert", "profile: expert-invalid"))
        self.must_reject()

    def test_heading_prefix_is_not_required_heading(self):
        path = self.state / "PROJECT.md"
        path.write_text(path.read_text().replace("## Data\n", "## Database\n"))
        self.must_reject()

    def test_unterminated_bad_finding_control(self):
        self.put("REVIEWS.md", "- [ ] CRITICAL | broken")
        self.must_reject()


class FixtureOracle(unittest.TestCase):
    def test_case7_recorded_bucket_matches_source_algorithm(self):
        fixture = (REPO / "tests/pressure/harness/cases/case-7/fixture.md").read_text()
        rows = re.findall(r"^(\d{4}-\d{2}-\d{2}T[^|\s]+)\|(\d{4}-\d{2}-\d{2}T\S+)$",
                          fixture, re.MULTILINE)
        self.assertEqual(len(rows), 6, "Update the audit probe if fixture shape changes")
        totals = {}
        for start, end in rows:
            start = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
            end = datetime.datetime.fromisoformat(end.replace("Z", "+00:00"))
            year, week, _ = start.isocalendar()
            key = f"{year}-W{week:02d}"
            totals[key] = totals.get(key, 0) + (end - start).total_seconds() / 3600
        actual = {key: (min(hours, 40), max(hours - 40, 0)) for key, hours in totals.items()}
        recorded = {key: (float(regular), float(overtime)) for key, regular, overtime in
                    re.findall(r"week (\d{4}-W\d+): got regular=([\d.]+) overtime=([\d.]+)", fixture)}
        self.assertTrue(recorded, "Recorded oracle absent; update probe with executable fixture")
        self.assertEqual(actual, recorded,
                         "Recorded evidence disagrees with the supplied ISOWeek algorithm. "
                         "Repair the fixture/oracle together, not payroll code to fit false evidence.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
