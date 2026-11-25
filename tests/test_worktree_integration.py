import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


def git(root, *args, env=None, check=True):
    return subprocess.run(
        ["git", "-C", str(root), *map(str, args)],
        env=env,
        check=check,
        capture_output=True,
    )


class WorktreeIntegrationTest(unittest.TestCase):
    def test_transfer_final_files_preserves_both_indexes_and_local_edits(self):
        with tempfile.TemporaryDirectory(prefix="maps worktree ") as directory:
            scratch = Path(directory)
            integration = scratch / "integration checkout"
            worker = scratch / "worker checkout"
            git(REPO, "clone", "--local", "--no-hardlinks", REPO, integration)
            git(integration, "worktree", "add", "--detach", worker, "HEAD")

            (worker / "README.md").write_bytes(b"A staged version\n")
            git(worker, "add", "README.md")
            (worker / "README.md").write_bytes(b"The final working version\n")
            (worker / "CHANGELOG.md").rename(worker / "renamed log.md")
            (worker / "LICENSE").unlink()
            binary = bytes(range(256))
            (worker / "new [binary].bin").write_bytes(binary)
            (worker / "outside-scope.txt").write_bytes(b"Retain only in worker\n")
            worker_index = git(worker, "ls-files", "--stage").stdout

            (integration / ".gitignore").write_bytes(b"# Integration-only staged change\n")
            git(integration, "add", ".gitignore")
            integration_index = git(integration, "ls-files", "--stage").stdout
            (integration / "local notes.txt").write_bytes(b"Keep local notes\n")

            patch = scratch / "task.patch"
            env = {**os.environ, "GIT_INDEX_FILE": str(scratch / "temporary index")}
            paths = ["README.md", "CHANGELOG.md", "renamed log.md", "LICENSE", "new [binary].bin"]
            git(worker, "read-tree", "HEAD", env=env)
            git(worker, "--literal-pathspecs", "add", "-A", "--", *paths, env=env)
            git(
                worker, "--literal-pathspecs", "diff", "--cached", "--binary", "--full-index",
                "--no-renames", "--no-ext-diff", "--no-textconv", f"--output={patch}",
                "HEAD", "--", *paths, env=env,
            )

            conflicting = integration / "new [binary].bin"
            conflicting.write_bytes(b"Existing local file\n")
            self.assertNotEqual(git(integration, "apply", "--check", patch, check=False).returncode, 0)
            self.assertEqual(conflicting.read_bytes(), b"Existing local file\n")
            self.assertTrue((integration / "LICENSE").exists())
            conflicting.unlink()

            git(integration, "apply", "--check", patch)
            git(integration, "apply", patch)
            self.assertEqual((integration / "README.md").read_bytes(), b"The final working version\n")
            self.assertEqual(conflicting.read_bytes(), binary)
            self.assertFalse((integration / "CHANGELOG.md").exists())
            self.assertFalse((integration / "LICENSE").exists())
            self.assertEqual(
                (integration / "renamed log.md").read_bytes(), (worker / "renamed log.md").read_bytes()
            )
            self.assertFalse((integration / "outside-scope.txt").exists())
            self.assertEqual((integration / "local notes.txt").read_bytes(), b"Keep local notes\n")
            self.assertEqual((integration / ".gitignore").read_bytes(), b"# Integration-only staged change\n")
            self.assertEqual(git(worker, "ls-files", "--stage").stdout, worker_index)
            self.assertEqual(git(integration, "ls-files", "--stage").stdout, integration_index)


if __name__ == "__main__":
    unittest.main()
