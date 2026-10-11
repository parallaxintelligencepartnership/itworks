import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from support import REPO
sys.path.insert(0,str(REPO/'tests/support'))
from validate_release_matrix import validate, REQUIRED


class ReleaseMatrix(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'observed.txt').write_text('synthetic recorded evidence\n')
        digest=hashlib.sha256((self.root/'observed.txt').read_bytes()).hexdigest()
        self.matrix={'schema_version':1,'candidate':'a'*40,'cells':[
            {'id':name,'candidate':'a'*40,'status':'PASS','command':'synthetic check',
             'checks':{'passed':1,'failed':0,'skipped':0},'reviewer':'independent-fixture','evidence':'observed.txt','sha256':digest}
            for name in REQUIRED]}

    def test_valid_synthetic_matrix(self):
        self.assertTrue(validate(self.matrix,self.root))

    def test_required_not_run_never_passes(self):
        self.matrix['cells'][0]['status']='NOT RUN'
        with self.assertRaisesRegex(ValueError,'NOT RUN'):validate(self.matrix,self.root)

    def test_missing_duplicate_wrong_candidate(self):
        for mutation in ('missing','duplicate','candidate'):
            matrix=copy.deepcopy(self.matrix)
            if mutation=='missing':matrix['cells'].pop()
            elif mutation=='duplicate':matrix['cells'].append(matrix['cells'][0])
            else:matrix['cells'][0]['candidate']='b'*40
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):validate(matrix,self.root)

    def test_modified_or_escaping_evidence(self):
        self.matrix['cells'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):validate(self.matrix,self.root)
        self.matrix['cells'][0]['evidence']='../outside'
        with self.assertRaises(ValueError):validate(self.matrix,self.root)

    def test_skipped_or_failed_checks_cannot_hide_under_pass(self):
        for key in ('failed','skipped'):
            matrix=copy.deepcopy(self.matrix);matrix['cells'][0]['checks'][key]=1
            with self.assertRaises(ValueError):validate(matrix,self.root)

    def test_review_failure_and_skip_counts_require_integers(self):
        for key,value in (('failed',False),('skipped',0.0)):
            matrix=copy.deepcopy(self.matrix)
            matrix['cells'][0]['checks'][key]=value
            with self.subTest(key=key,value=value),self.assertRaisesRegex(ValueError,'checks'):
                validate(matrix,self.root)
