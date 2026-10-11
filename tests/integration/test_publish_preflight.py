"""Execute the documented counts preflight under strict shell settings."""
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'unit'))
from support import REPO, StateProject, run


class PublishPreflight(StateProject):
    def test_documented_counts_strict_shell(self):
        body = (REPO / 'references/publish.md').read_text()
        section = body.split('<!-- executable: publish-counts -->')[1].split('<!-- /executable: publish-counts -->')[0]
        script = re.search(r'```bash\n(.*?)```', section, re.S).group(1)
        result = run(['/bin/bash', '-euo', 'pipefail', '-c', script + '\nprintf "%s\\n" "$counts"'], env={'plugin_root':str(REPO),'project_root':str(self.root)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '0 0 0 0 0')
        self.put('REVIEWS.md', '* [ ] CRITICAL | broken\n')
        result = run(['/bin/bash', '-euo', 'pipefail', '-c', script + '\necho MUST_NOT_PUBLISH'], env={'plugin_root':str(REPO),'project_root':str(self.root)})
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('MUST_NOT_PUBLISH', result.stdout)

    def test_bounded_id_under_pipefail(self):
        body = (REPO / 'references/publish.md').read_text()
        script = re.search(r'```\n(# Bounded input.*?)```', body, re.S).group(1)
        result = run(['/bin/bash','-euo','pipefail','-c', script + '\nprintf "%s" "$id"'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r'^[a-z2-7]{12}$')

    def test_incomplete_or_duplicate_protocol_rejected(self):
        body = (REPO / 'references/publish.md').read_text()
        section = body.split('<!-- executable: publish-counts -->')[1].split('<!-- /executable: publish-counts -->')[0]
        script = re.search(r'```bash\n(.*?)```', section, re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'scripts').mkdir()
            for payload in ('FORMAT\t1\n', 'FORMAT\t1\nSUMMARY\t0\t0\t0\n', 'FORMAT\t1\nCOUNT\tfound\t0\nCOUNT\tfound\t0\nSUMMARY\t0\t0\t0\n'):
                (root/'scripts/itworks-state.sh').write_text("cat <<'DATA'\n"+payload+'DATA\n')
                result = run(['/bin/bash','-euo','pipefail','-c',script],env={'plugin_root':str(root),'project_root':str(self.root)})
                self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__': unittest.main()

class PublicationData(unittest.TestCase):
    def test_documented_message_and_pr_treat_fields_as_data(self):
        import subprocess
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for args in (['git','init','-q'],['git','config','user.name','Fixture'],['git','config','user.email','fixture@example.invalid']):
                self.assertEqual(run(args,cwd=root).returncode,0)
            (root/'entry.json').write_text('{}\n');run(['git','add','--','entry.json'],cwd=root)
            title='entry: $(touch injected) `touch injected2` "quoted"'
            body='summary: literal $(touch injected3) "data"\n'
            message=root/'message.txt';message.write_text(title+'\n')
            bodyfile=root/'body.txt';bodyfile.write_text(body)
            bindir=root/'bin';bindir.mkdir()
            mock=bindir/'gh'
            mock.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$ARG_LOG"\n');mock.chmod(0o700)
            doc=(REPO/'references/publish.md').read_text()
            def block(name):
                part=doc.split('<!-- executable: '+name+' -->')[1].split('<!-- /executable: '+name+' -->')[0]
                return re.search(r'```bash\n(.*?)```',part,re.S).group(1)
            result=run(['/bin/bash','-euo','pipefail','-c',block('publish-message')+'\n'+block('publish-pr')],cwd=root,env={'message_file':str(message),'body_file':str(bodyfile),'PATH':str(bindir)+os.pathsep+os.environ['PATH'],'ARG_LOG':str(root/'args.txt')})
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(run(['git','log','-1','--format=%B'],cwd=root).stdout.strip(),title)
            args=(root/'args.txt').read_text().splitlines()
            self.assertEqual(args[args.index('--title')+1],title)
            self.assertEqual(args[args.index('--body-file')+1],str(bodyfile))
            self.assertEqual(bodyfile.read_text(),body)
            self.assertFalse(any(root.glob('injected*')))
