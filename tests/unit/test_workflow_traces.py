"""Developer trace oracle: does not establish live skill compliance."""
import json
import re
import unittest
from support import REPO

DATA = json.loads((REPO/'tests/fixtures/workflow/transitions.json').read_text())


def select(debt, applicable, context):
    overdue = sorted((i for i in range(5) if applicable[i] and debt[i]>=3),key=lambda i:(-debt[i],i))
    selected = (overdue + [i for i in range(5) if applicable[i] and i in context and i not in overdue])[:2]
    return selected, [0 if not applicable[i] or i in selected else debt[i]+1 for i in range(5)]


class WorkflowTrace(unittest.TestCase):
    def test_schedule_overflow_and_nonapplicable(self):
        for row in DATA['scheduling']:
            self.assertEqual(select(row['debt'],row['applicable'],row['context']), (row['selected'],row['next']))

    def test_completed_scope_only(self):
        for row in DATA['audits']:
            marker = row['candidate'] if set(row['scope'])<=set(row['read']) and not row.get('required_verification_unavailable') else row['old']
            self.assertEqual(marker,row['expected'])

    def test_closeout_instruction_phase_order(self):
        # Structural instruction regression, independently traced by reviewer;
        # actual gate operations are covered by integration tests.
        text=(REPO/'skills/project-closeout/SKILL.md').read_text()
        self.assertIn('## Step 0: Applicability', text)
        self.assertIn('## Step 3: Ship checklist', text)
        self.assertIn('## Step 4: The reckoning', text)
        self.assertLess(text.index('## Step 0: Applicability'),text.index('## Step 1: Full sweep'))
        self.assertLess(text.index('## Step 3: Ship checklist'),text.index('## Step 4: The reckoning'))
        self.assertLess(text.index('## Step 4: The reckoning'),text.index('## Step 5: Write SHIPPED.md'))

    def test_matching_lockfile_only(self):
        mapping={'Cargo.toml':{'Cargo.lock'},'composer.json':{'composer.lock'}}
        for row in DATA['lockfiles']:
            self.assertEqual(bool(mapping[row['manifest']] & set(row['tracked'])),row['valid'])
