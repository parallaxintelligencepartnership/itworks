"""Known mixed workloads must exercise open, closed and archived count semantics."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('state_benchmark',ROOT/'tests/benchmarks/state_lint.py')
benchmark=importlib.util.module_from_spec(spec);spec.loader.exec_module(benchmark)

class BenchmarkWorkloads(unittest.TestCase):
    def test_known_mixed_workload_counts(self):
        for distribution,expected_fixed,expected_open in [('active',5,5),('archived',9,1)]:
            with self.subTest(distribution=distribution),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)/'project'
                benchmark.make_workload(root,10,distribution,ROOT/'tests/fixtures/state/v3')
                live=(root/'.itworks/REVIEWS.md').read_text()
                self.assertEqual(live.count('- [ ] IMPORTANT'),expected_open)
                for archive in (root/'.itworks/archive').glob('*'):
                    self.assertNotIn('- [ ]',archive.read_text())
                actual,scope=benchmark.counts(ROOT,root)
                self.assertEqual(scope,'candidate-lifetime')
                self.assertEqual(actual,dict(found=10,fixed=expected_fixed,accepted=0,critical_open=0,critical_accepted=0))

    def test_actual_child_cpu_is_measured_and_summarized(self):
        import sys
        child='import time\nstart=time.process_time()\nwhile time.process_time()-start < 0.05: pass\n'
        result,elapsed=benchmark.command([sys.executable,'-c',child])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(hasattr(result,'child_cpu'),'benchmark omits available child CPU measurements')
        cpu=result.child_cpu
        self.assertEqual(cpu['status'],'AVAILABLE')
        self.assertGreater(cpu['total_seconds'],0.03)
        self.assertGreaterEqual(cpu['user_seconds'],0)
        self.assertGreaterEqual(cpu['system_seconds'],0)
        self.assertAlmostEqual(cpu['total_seconds'],cpu['user_seconds']+cpu['system_seconds'])
        rows=[dict(distribution='active',size=0,artifact='candidate',phase='measured',seconds=elapsed,exit_status=0,classification=[0,0],child_cpu=cpu)]
        summary=benchmark.summarize(rows)[0]
        self.assertIn('child_cpu',summary,'summary omits process CPU metrics')
        for metric in ('user_seconds','system_seconds','total_seconds'):
            for statistic in ('median','p95','min','max'):
                self.assertEqual(summary['child_cpu'][metric][statistic],cpu[metric])
