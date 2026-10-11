#!/usr/bin/env python3
"""Run historical RED and isolated candidate mutations; never modify source checkout."""
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/unit'))
import support
import test_state_contract


def execute(names=None):
    stream=io.StringIO()
    suite=(unittest.TestSuite(test_state_contract.StateContract(name) for name in names) if names
           else unittest.defaultTestLoader.loadTestsFromTestCase(test_state_contract.StateContract))
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    return result,stream.getvalue()

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: sensitivity.py OUTPUT_FILE')
    report=[]
    with tempfile.TemporaryDirectory(prefix='itworks-sensitivity-') as tmp:
        root=Path(tmp);(root/'scripts').mkdir();(root/'tests/fixtures').mkdir(parents=True)
        shutil.copytree(ROOT/'tests/fixtures/state',root/'tests/fixtures/state')
        (root/'scripts/itworks-lint.sh').write_bytes(subprocess.check_output(['git','show',
            '7df722830da8fe3a3872459e06308d2d53f4153b:scripts/itworks-lint.sh'],cwd=ROOT))
        support.REPO=root
        result,output=execute()
        assert len(result.failures)==5 and not result.errors
        report.append('ACTUAL AUDITED ARTIFACT: 5 intended assertions fail, 3 controls pass\n'+output)
        for file in ('itworks-lint.sh','itworks-state.sh','itworks-state.awk'):
            shutil.copy2(ROOT/'scripts'/file,root/'scripts'/file)
        path=root/'scripts/itworks-state.awk';source=path.read_text()
        mutations=[
            ('ship critical condition','if(live_critical)','if(0)',['test_canonical_critical_control']),
            ('complete profile scalar','/^(guided|brief|expert)$/','/^(guided|brief|expert)/',['test_profile_requires_complete_enum']),
            ('empty acceptance section','if (accept_n && !entries)','if (0)',['test_empty_acceptance_is_not_a_waiver']),
            ('broad candidate discovery','if ($0 ~ /^[ \\t]*[-*+][ \\t]+\\[[ xX]\\]/)',
             'if ($0 ~ /^- \\[[ xX]\\]/)', ['test_indented_critical_must_not_disappear','test_alternate_bullet_critical_must_not_disappear']),
            ('exact project heading','heads[file SUBSEP heading($0)]=1',
             'heads[file SUBSEP heading($0)]=1; if(file==".itworks/PROJECT.md" && $0=="## Database") heads[file SUBSEP "## Data"]=1',
             ['test_heading_prefix_is_not_required_heading'])]
        for name,before,after,tests in mutations:
            assert before in source,('mutation target changed',name)
            path.write_text(source.replace(before,after))
            result,output=execute(tests)
            assert len(result.failures)==len(tests) and not result.errors,(name,output)
            report.append('DISPOSABLE MUTATION '+name+'\nReplace '+repr(before)+' with '+repr(after)+'\n'+output)
            path.write_text(source)
        result,output=execute();assert result.wasSuccessful()
        report.append('RESTORED DISPOSABLE CANDIDATE: all8 GREEN\n'+output)
    support.REPO=ROOT
    Path(sys.argv[1]).write_text('\n'.join(report))
    print('Historical5 RED; five isolated mutations/six intended assertion RED; restored8 GREEN.')

if __name__=='__main__':main()
