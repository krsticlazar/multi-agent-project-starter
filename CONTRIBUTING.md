# Contributing

Keep public repository content in English. Put installable project files under `template/`, distribution scripts under `scripts/`, starter user documentation under `guides/`, and focused checks under `tests/`. Keep native settings minimal and shared behavior in a provider-independent source whenever possible.

## Changes

- Keep project requirements, plans, and memory independent of provider session history.
- Put provider-specific arguments only where the current supported formats need them. Link to the provider's documentation and state the version and environment used for any local verification.
- Run the focused checks in disposable directories. The suite uses the Python standard library and Git to check direct and archive-based installation, local runtime state, and worktree integration.

  ```sh
  python -B -m unittest discover -s tests -v
  ```

- Run `git diff --check`. Review new files for secrets, session IDs, runtime data, and unrelated changes. Keep `.runtime/` local. See [verification notes](guides/VERIFICATION.md) for the other checks.

## Versioned archives

Use Conventional Commits and Semantic Versioning with `vX.Y.Z` tags. Keep changes under **Unreleased** in [the changelog](CHANGELOG.md) until a release owner assigns a version. The package is a source snapshot that includes the installer and the `template/` payload. The installer copies only `template/`. GitHub can generate ZIP and tar archives from the chosen tag. The following command prepares a ZIP from an existing tag without a remote action.

```sh
git archive --format=zip --prefix=multi-agent-project-starter-vX.Y.Z/ -o multi-agent-project-starter-vX.Y.Z.zip vX.Y.Z
```

Substitute a real tag. Before publishing, inspect the archive for `.git` metadata, runtime artifacts, and credentials. Extract it into a scratch location and run the installer from there. A project owner performs commits, pushes, tags, and release publication. Agents can prepare the change and propose a commit message.
