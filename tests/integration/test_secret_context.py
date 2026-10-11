import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
from support import REPO,run

class SecretContext(unittest.TestCase):
    def test_context_and_redacted_prescribed_scans(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                result=run(['git','-C',root,*args]); self.assertEqual(result.returncode,0,result.stderr); return result
            git('init','-q'); git('config','user.email','fixture@example.invalid'); git('config','user.name','Fixture')
            token='sk-proj-'+'SYNTHETICONLY123456789'
            (root/'.gitignore').write_text('.env\n')
            (root/'.env').write_text(token+'\n')
            (root/'.env.example').write_text('API_KEY=<your-key>\n')
            (root/'public').mkdir(); (root/'public/app.js').write_text(token+'\n')
            git('add','.gitignore','.env.example','public/app.js'); git('commit','-qm','fixture')
            # Private config: ignored + untracked; fixture's sole served root public.
            self.assertEqual(run(['git','-C',root,'check-ignore','.env']).returncode,0)
            self.assertNotEqual(run(['git','-C',root,'ls-files','--error-unmatch','.env']).returncode,0)
            self.assertNotEqual(run(['grep','-Eq','-f',REPO/'references/secret-patterns.grep',root/'.env.example']).returncode,0)
            (root/'.env.example').write_text(token+'\n')
            self.assertEqual(run(['grep','-Eq','-f',REPO/'references/secret-patterns.grep',root/'.env.example']).returncode,0)
            document=(REPO/'references/lens-security-auth.md').read_text()
            def prescribed(label):
                return re.search(r'# '+label+r'\n([^`]+)```',document).group(1).strip()
            env={'PAT':str(REPO/'references/secret-patterns.grep')}
            result=run(['/bin/bash','-o','pipefail','-c',prescribed('secret-candidate-scan')],cwd=root,env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('public/app.js:1',result.stdout); self.assertIn('.env:1',result.stdout)
            self.assertTrue(token not in result.stdout+result.stderr,'retained output contained credential-shaped fixture text')
            (root/'public/app.js').write_text('clean\n'); git('add','public/app.js'); git('commit','-qm','remove fixture')
            result=run(['/bin/bash','-o','pipefail','-c',prescribed('secret-history-scan')],cwd=root,env=env)
            self.assertEqual(result.returncode,0,result.stderr); self.assertRegex(result.stdout,r'\d+\n')
            self.assertTrue(token not in result.stdout+result.stderr,'retained output contained credential-shaped fixture text')
