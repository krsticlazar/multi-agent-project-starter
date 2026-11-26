# Worktree integration

Use linked Git worktrees for concurrent writers when their file scopes can be isolated. Read-only research, planning, and review can use the integration checkout. The Develop Boss coordinates paths and worktrees. The Orchestrator owns integration and updates the canonical task index and memory.

## Isolate the work

1. Record the integration checkout's `git status --short` and `git rev-parse HEAD` before assigning the task. Use an existing commit as the worker's base.
2. From the integration checkout, run `git worktree add -b codex/task-001 ../project-task-001 HEAD`. Give the worker the assigned paths, task document reference, and integration checkout path.
3. Keep `tasks/INDEX.md`, `MEMORY.md`, and the project runtime in the integration checkout. The worker works from a task snapshot and sends changes or checkpoints back. Changes in separate worktrees are independent until integrated.
4. Ask the worker for its exact changed paths, including each new file and both sides of a rename. Inspect its status and diff. Include only assigned paths in the transfer. Ask about ambiguous ownership before proceeding.

## Local-only workflow records

Before launching a role from a linked worktree, give it the primary checkout path, assigned scope, and exact paths for the local role briefing and shared records. If the client requires a briefing in its own root, transfer only the authorized files and verify that they are ignored before any staging. If the helper is absent, run `python PRIMARY/tools/session.py --cwd WORKTREE status` with the actual paths to check access. Keep shared state in the primary checkout and verify access on the intended client. For a fresh clone restore the approved local setup from the owner's private copy. [Local-only Git setup](GIT_SETUP.md#opt-into-local-only-workflow-records)

## Transfer uncommitted files

Prepare a binary-capable patch from the worker's actual working files against its `HEAD`. The temporary Git index starts at that commit and captures the final versions of tracked, deleted, and new non-ignored files. The worker's own staging remains intact. For a rename, the patch carries both paths as a deletion and an addition.

Use an absolute patch path outside both checkouts. Replace the sample paths and keep both endpoints of any rename in the list. Treat an unexpected empty patch or failed command as a reason to stop and inspect.

```bash
worker=/absolute/path/project-task-001
patch=/absolute/path/task-001.patch
paths=(file-to-edit path/to/new-file old-name new-name file-to-delete)
(
  set -e
  scratch=$(mktemp -d)
  trap 'rm -f -- "$scratch/index"; rmdir -- "$scratch"' EXIT
  export GIT_INDEX_FILE="$scratch/index"
  git --literal-pathspecs -C "$worker" read-tree HEAD
  git --literal-pathspecs -C "$worker" add -A -- "${paths[@]}"
  git --literal-pathspecs -C "$worker" diff --cached --binary --full-index \
    --no-renames --no-ext-diff --no-textconv --output="$patch" HEAD -- "${paths[@]}"
)
```

```powershell
$worker = 'C:/path/project-task-001'
$patch = 'C:/path/task-001.patch'
$paths = @('file-to-edit', 'path/to/new-file', 'old-name', 'new-name', 'file-to-delete')
$index = Join-Path ([IO.Path]::GetTempPath()) ('task-index-' + [guid]::NewGuid())
$previousIndex = $env:GIT_INDEX_FILE
try {
    $env:GIT_INDEX_FILE = $index
    git --literal-pathspecs -C $worker read-tree HEAD
    if ($LASTEXITCODE) { throw 'Could not initialize the task index.' }
    git --literal-pathspecs -C $worker add -A -- $paths
    if ($LASTEXITCODE) { throw 'Could not capture the assigned files.' }
    git --literal-pathspecs -C $worker diff --cached --binary --full-index `
        --no-renames --no-ext-diff --no-textconv "--output=$patch" HEAD -- $paths
    if ($LASTEXITCODE) { throw 'Could not write the task patch.' }
} finally {
    $env:GIT_INDEX_FILE = $previousIndex
    Remove-Item -LiteralPath $index -ErrorAction SilentlyContinue
}
```

In the integration checkout, inspect the patch with `git apply --stat <patch>` and review the actual diff. Run `git apply --check <patch>` and, after a successful check with no concurrent writes to those paths, `git apply <patch>`. Use the default apply mode so it leaves the integration index alone. On a failed check, preserve the patch and worker files. Reconcile the conflicting paths with the existing edits, then verify the final diff and run the task checks. Avoid partial application with `--reject`.

Ignored files, submodule contents, and a path's earlier staged version are outside this patch. Record anything needed for handoff separately and transfer it only within the approved scope. Preserve the worker worktree until the integrated changes are verified or safely saved. Follow the [approved checkpoint procedure](GIT_SETUP.md#publish-an-approved-checkpoint).
