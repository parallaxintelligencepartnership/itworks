from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unit'))
from support import run,REPO

class CheckpointStaging(unittest.TestCase):
    def test_actual_path_limited_commit_preserves_unrelated_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                r=run(['git','-C',root,*args]); self.assertEqual(r.returncode,0,r.stderr); return r.stdout
            git('init','-q'); git('config','user.email','fixture@example.invalid'); git('config','user.name','Fixture')
            for name in ('task.py','unrelated','unstaged'): (root/name).write_text('base\n')
            git('add','task.py','unrelated','unstaged'); git('commit','-qm','fixture')
            (root/'task.py').write_text('candidate\n'); (root/'reviews.md').write_text('task review\n')
            (root/'unrelated').write_text('staged\n'); git('add','unrelated')
            (root/'unrelated').write_text('staged plus unstaged\n'); (root/'unstaged').write_text('other work\n')
            (root/'credential-note').write_text('sk-proj-SYNTHETICONLY123456789\n')
            before=git('ls-files','--stage','unrelated'); content=(root/'unrelated').read_bytes()
            # Execute exact documented block, populated only by reviewed owned paths.
            doc=(REPO/'skills/project-checkpoint/SKILL.md').read_text()
            code=doc.split('# checkpoint-owned-commit (owned_paths is a reviewed Bash array)\n',1)[1].split('```',1)[0]
            result=run(['/bin/bash','-eu','-c','owned_paths=(task.py reviews.md)\ncheckpoint_message=checkpoint\n'+code],cwd=root)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(set(git('diff-tree','--no-commit-id','--name-only','-r','HEAD').splitlines()),{'task.py','reviews.md'})
            self.assertEqual(git('ls-files','--stage','unrelated'),before)
            self.assertEqual((root/'unrelated').read_bytes(),content)
            self.assertEqual((root/'unstaged').read_text(),'other work\n')
            self.assertNotIn('credential-note',git('ls-tree','-r','--name-only','HEAD'))

    def test_literal_task_filename_does_not_expand_pathspec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                result=run(['git','-C',root,*args]);self.assertEqual(result.returncode,0,result.stderr);return result.stdout
            git('init','-q');git('config','user.email','fixture@example.invalid');git('config','user.name','Fixture')
            for name in ('task[1].py','task1.py'):(root/name).write_text('base\n')
            git('add','--','.');git('commit','-qm','fixture')
            for name in ('task[1].py','task1.py'):(root/name).write_text('changed\n')
            doc=(REPO/'skills/project-checkpoint/SKILL.md').read_text()
            code=doc.split('# checkpoint-owned-commit (owned_paths is a reviewed Bash array)\n',1)[1].split('```',1)[0]
            result=run(['/bin/bash','-eu','-c',"owned_paths=('task[1].py')\ncheckpoint_message=checkpoint\n"+code],cwd=root)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(git('diff-tree','--no-commit-id','--name-only','-r','HEAD').splitlines(),['task[1].py'])
            self.assertEqual((root/'task1.py').read_text(),'changed\n')
            self.assertEqual(git('show','HEAD:task1.py'),'base\n')
