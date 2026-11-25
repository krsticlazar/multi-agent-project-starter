# Multi-Agent Project Starter

A lightweight, provider-agnostic starter template for multi-agent AI development.

When several coding agents share a project, requirements, decisions, and handoffs can get buried in their chats. This starter keeps that knowledge in the project and assigns one owner to each shared document. Agents load the rules and files needed for their own assignment. Small tasks can take a direct path, and larger phases can delegate through specialist roles and Git worktrees.

Use OpenAI Codex, Claude Code, or both with your existing subscription access. A mixed setup can use Codex for daily development and Claude for architecture and complex consultations. One provider is sufficient. The starter uses Markdown, native agent definitions, and an optional local session helper.

## Quick start

1. Get a source archive from the repository, extract it, and open a shell in the extracted directory. For a reproducible download, select a published `vX.Y.Z` tag or an implementation commit before using **Code → Download ZIP**. [GitHub source archives](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)
2. Run the installer for your shell. Choose an existing directory or a new directory whose parent already exists.

   **Windows with PowerShell**

   ```powershell
   .\scripts\install.ps1 -Destination 'C:\Projects\my-app'
   ```

   **Linux or macOS with Bash**

   ```bash
   bash scripts/install.sh "$HOME/projects/my-app"
   ```

3. Open a new Codex or Claude Code session from the destination. Select a model appropriate for setup, such as GPT-6.2 Sol with medium reasoning or Sonnet with medium effort, if available to your account. Send this prompt.

   ```text
   Read ASK_ME.md and follow its instructions to initialize and configure this project.
   ```

Bootstrap records your language, project scope, provider, models, and optional tools. It prepares a Director handoff and either opens a Director through an available supported mechanism or gives you a prompt to open a new session yourself. Use the real session ID or link when the client exposes one.

You need one signed-in AI coding client. Git is needed for worktrees, and Python 3.10 or newer is needed for the optional session helper. PowerShell and Bash install paths have been exercised on Windows. See [Getting started](guides/GETTING_STARTED.md) and [verification results](guides/VERIFICATION.md) for platform and transport details.

## Existing projects

The installer copies files from `template/`, including hidden provider directories. It preserves existing files and Git configuration, reports collisions as `Kept existing`, and leaves installation sources outside the target. Review each collision before Bootstrap and merge the relevant instructions deliberately. In particular, review any existing `AGENTS.md`, `CLAUDE.md`, provider settings, project memory, and plan. Bootstrap protects the local runtime before writing state even when an existing `.gitignore` is preserved.

## Workflow

1. **Director** clarifies requirements in your preferred language and records deferred ideas in `tasks/QUEUE.md`.
2. **Planner** proposes architecture, milestones, and acceptance criteria. Director brings the plan to you for approval.
3. **Orchestrator** coordinates approved work, maintains the task index and project memory, and consolidates reports. Research, Develop, and Review Bosses can coordinate scoped workers and native subagents when the work warrants them.
4. **Supervisor** helps with hard decisions on demand. Director reports outcomes and asks for decisions that require your approval.

The project documents carry progress across sessions. Local Codex agents can send a `TASK` or `REPORT` through the native queue to wake a registered session. The local relay preserves pending messages and records one recipient receipt. On a usage limit, stop new project work, checkpoint the current changes, and wait for explicit approval to resume. See [the operational workflow](template/docs/WORKFLOW.md) and [session communication](template/docs/COMMUNICATION.md).

## Project files

| Path | Purpose |
| --- | --- |
| `ASK_ME.md`, `AGENTS.md`, `CLAUDE.md` | First-run setup and shared rules |
| `PROJECT.md`, `MEMORY.md`, `PLAN.md` | Requirements, current knowledge, and approved work |
| `docs/` | Architecture, decisions, workflow, roles, models, and tools |
| `tasks/` | Task index, idea queue, and task records |
| `.codex/`, `.claude/`, `.agents/skills/` | Native configuration and skills |
| `tools/session.py`, `.runtime/` | Optional helper and local state created during setup |

Human owners commit, push, tag, and publish. Agents can prepare changes and use [isolated worktrees](template/docs/WORKTREES.md) for parallel work. The starter stores no provider credentials and operates no telemetry or relay service. Selected providers and third-party tools process data under their own terms.

## Guides

- [Getting started and upgrading](guides/GETTING_STARTED.md)
- [Choosing models and effort](guides/MODELS.md)
- [Optional plugins, MCP servers, and skills](guides/PLUGINS.md)
- [Troubleshooting](guides/TROUBLESHOOTING.md)
- [Contributing and packaging](CONTRIBUTING.md)

## License

[MIT](LICENSE)
