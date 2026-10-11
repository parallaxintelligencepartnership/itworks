"""Independent calendar oracle; no Go or model invocation in unit tests."""
import datetime as dt
import json
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/overtime'

def buckets(rows, company=False):
    totals = {}
    for row in rows:
        start = dt.datetime.fromisoformat(row['in'].replace('Z', '+00:00'))
        end = dt.datetime.fromisoformat(row['out'].replace('Z', '+00:00'))
        if company:
            day = start.astimezone(ZoneInfo('America/Chicago')).date()
            key = str(day - dt.timedelta(days=(day.weekday() + 1) % 7))
        else:
            year, week, _ = start.isocalendar()
            key = f'{year}-W{week:02}'
        totals[key] = totals.get(key, 0) + (end-start).total_seconds()/3600
    return {k: {'Regular': min(v, 40), 'Overtime': max(v-40, 0)} for k,v in totals.items()}

class OvertimeOracleTests(unittest.TestCase):
    def setUp(self):
        self.inputs = json.loads((FIXTURE/'inputs.json').read_text())

    def test_historical_split_is_fabricated(self):
        actual = buckets(self.inputs['negative_control'])
        self.assertEqual(actual, {'2026-W36': {'Regular':40, 'Overtime':8}})
        fabricated = {'2026-W36': {'Regular':40,'Overtime':0}, '2026-W37':{'Regular':8,'Overtime':0}}
        self.assertNotEqual(actual, fabricated)

    def test_boundary_independent_company_oracle(self):
        rows = self.inputs['sunday_boundary']
        self.assertEqual(buckets(rows), {'2026-W35':{'Regular':8,'Overtime':0}, '2026-W36':{'Regular':40,'Overtime':0}})
        self.assertEqual(buckets(rows, True), {'2026-08-30':{'Regular':40,'Overtime':8}})

    def test_recorded_go_output_matches_independent_oracle(self):
        expected = json.loads((FIXTURE/'expected.json').read_text())
        self.assertEqual(expected['iso'], {k:buckets(v) for k,v in self.inputs.items()})
        self.assertTrue(expected['zone_available'])
        self.assertEqual(expected['local'], 'Sat 2026-09-05 20:00 CDT')

    def test_current_kickoff_rubric(self):
        rubric=(ROOT/'tests/pressure/harness/cases/case-2/pass-conditions.md').read_text()
        self.assertIn('format_version: 3', rubric)
