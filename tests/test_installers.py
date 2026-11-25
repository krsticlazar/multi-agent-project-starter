import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile


REPO = Path(__file__).resolve().parents[1]


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


def installers():
    if os.name == 'nt':
        git_root = Path(run('git', '--exec-path').strip()).parents[2]
        bash = git_root / 'bin' / 'bash.exe'
        if bash.is_file():
            yield [str(bash)], 'install.sh'
    elif shutil.which('bash'):
        yield ['bash'], 'install.sh'
    for powershell in ('powershell', 'pwsh'):
        if shutil.which(powershell):
            yield [powershell, '-NoProfile', '-NonInteractive', '-File'], 'install.ps1'


def link_directory(target, link):
    if os.name == 'nt':
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)


class InstallerTests(unittest.TestCase):
    def test_source_archive_and_safe_installation(self):
        shells = list(installers())
        self.assertTrue(shells, 'At least one supported installer shell is required.')
        with tempfile.TemporaryDirectory(prefix='starter install test ') as temporary:
            scratch = Path(temporary)
            source = scratch / 'source bundle'
            shutil.copytree(REPO / 'scripts', source / 'scripts')
            shutil.copyfile(REPO / '.gitignore', source / '.gitignore')
            template = source / 'template'
            files = {
                '.gitignore': '/.runtime/\n',
                'ASK_ME.md': 'Bootstrap instructions\n',
                'AGENTS.md': 'Shared instructions\n',
                '.claude/agents/director.md': 'Claude agent\n',
                '.codex/agents/director.toml': 'Codex agent\n',
                '.agents/skills/checkpoint/SKILL.md': 'Shared skill\n',
                '.runtime/state.json': 'local fixture\n',
                '.claude/settings.local.json': 'local fixture\n',
                '.env.local': 'local fixture\n',
            }
            for relative, contents in files.items():
                file = template / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(contents, encoding='utf-8')

            run('git', 'init', '--quiet', str(source))
            run('git', '-C', str(source), 'add', '.')
            tree = run('git', '-C', str(source), 'write-tree').strip()
            archive = scratch / 'source snapshot.zip'
            run('git', '-C', str(source), 'archive', '--format=zip', '--prefix=bundle/', '-o', str(archive), tree)
            with zipfile.ZipFile(archive) as package:
                entries = package.namelist()
                self.assertIn('bundle/template/.agents/skills/checkpoint/SKILL.md', entries)
                self.assertTrue(all('/.git/' not in entry and '/.runtime/' not in entry for entry in entries))
                self.assertNotIn('bundle/template/.env.local', entries)
                self.assertNotIn('bundle/template/.claude/settings.local.json', entries)
                package.extractall(scratch)

            for index, (shell, script_name) in enumerate(shells):
                with self.subTest(shell=shell[0]):
                    script = scratch / 'bundle' / 'scripts' / script_name
                    fresh = scratch / f'fresh project {index}'
                    run(*shell, str(script), str(fresh))
                    self.assertFalse((fresh / '.git').exists())
                    self.assertEqual((fresh / '.gitignore').read_text(), files['.gitignore'])
                    self.assertTrue((fresh / '.codex/agents/director.toml').is_file())
                    self.assertTrue((fresh / '.claude/agents/director.md').is_file())
                    self.assertTrue((fresh / '.agents/skills/checkpoint/SKILL.md').is_file())

                    existing = scratch / f'existing project {index}'
                    link_target = scratch / f'other directory {index}'
                    link_target.mkdir()
                    run('git', 'init', '--quiet', str(existing))
                    run('git', '-C', str(existing), 'remote', 'add', 'origin', 'https://example.invalid/project.git')
                    original_config = (existing / '.git/config').read_bytes()
                    (existing / 'AGENTS.md').write_bytes(b'User instructions\r\n')
                    (existing / '.gitignore').write_bytes(b'private-project-file\r\n')
                    (existing / '.codex').write_bytes(b'Blocked directory')
                    link_directory(link_target, existing / '.claude')

                    script = source / 'scripts' / script_name
                    output = run(*shell, str(script), str(existing))
                    self.assertIn('Kept existing AGENTS.md', output)
                    self.assertIn('Kept existing .gitignore', output)
                    self.assertEqual((existing / 'AGENTS.md').read_bytes(), b'User instructions\r\n')
                    self.assertEqual((existing / '.gitignore').read_bytes(), b'private-project-file\r\n')
                    self.assertEqual((existing / '.codex').read_bytes(), b'Blocked directory')
                    self.assertEqual((existing / '.git/config').read_bytes(), original_config)
                    self.assertEqual(list(link_target.iterdir()), [])
                    self.assertFalse((existing / '.runtime').exists())
                    self.assertFalse((existing / '.env.local').exists())
                    self.assertFalse((existing / '.claude/settings.local.json').exists())
                    self.assertTrue((existing / 'ASK_ME.md').is_file())
                    self.assertIn('Kept existing ASK_ME.md', run(*shell, str(script), str(existing)))
                    with self.assertRaises(subprocess.CalledProcessError):
                        run(*shell, str(script), str(template / 'bad destination'))
                    self.assertFalse((template / 'bad destination').exists())

    def test_reject_linked_template_overlap(self):
        with tempfile.TemporaryDirectory(prefix='starter link test ') as temporary:
            scratch = Path(temporary)
            source = scratch / 'source'
            template = source / 'template'
            template.mkdir(parents=True)
            shutil.copytree(REPO / 'scripts', source / 'scripts')
            alias = scratch / 'template alias'
            link_directory(template, alias)
            linked_source = scratch / 'linked source'
            shutil.copytree(REPO / 'scripts', linked_source / 'scripts')
            link_directory(template, linked_source / 'template')
            for shell, script_name in installers():
                with self.subTest(shell=shell[0]):
                    destination = alias / 'new child'
                    with self.assertRaises(subprocess.CalledProcessError):
                        run(*shell, str(source / 'scripts' / script_name), str(destination))
                    self.assertFalse(destination.exists())
                    with self.assertRaises(subprocess.CalledProcessError):
                        run(*shell, str(linked_source / 'scripts' / script_name), str(scratch / 'new target'))
                    self.assertFalse((scratch / 'new target').exists())

    def test_install_public_template(self):
        with tempfile.TemporaryDirectory(prefix='starter payload test ') as temporary:
            for index, (shell, script_name) in enumerate(installers()):
                with self.subTest(shell=shell[0]):
                    target = Path(temporary) / f'project {index}'
                    run(*shell, str(REPO / 'scripts' / script_name), str(target))
                    for relative in (
                        'ASK_ME.md',
                        'AGENTS.md',
                        'CLAUDE.md',
                        'docs/WORKFLOW.md',
                        'docs/COMMUNICATION.md',
                        '.codex/config.toml',
                        '.claude/settings.json',
                        '.agents/skills/project-checkpoint/SKILL.md',
                        'tools/session.py',
                    ):
                        self.assertEqual((target / relative).read_bytes(), (REPO / 'template' / relative).read_bytes())
                    self.assertFalse((target / '.runtime').exists())


if __name__ == '__main__':
    unittest.main()
