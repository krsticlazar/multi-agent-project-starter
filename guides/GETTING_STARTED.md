# Getting started

## Choose your environment

Install and sign in to at least one official client. For Codex CLI, use `codex --version` and `codex login status`. To sign in with a ChatGPT subscription, run `codex login`. For Claude Code, use `claude --version` and `claude auth status`. To sign in with a Claude subscription, use `claude auth login` or `/login` inside Claude Code. Account availability and organization policy determine which models and features are offered. [Codex authentication](https://learn.chatgpt.com/docs/auth) · [Claude Code CLI](https://code.claude.com/docs/en/cli-reference) · [Claude Code terms](https://code.claude.com/docs/en/legal-and-compliance)

Use compatible local runtimes across the project. Keep native Windows and WSL2 sessions separate unless you have explicitly verified the environment and transport. Git is optional for setup and required for worktrees. Python 3.10 or newer enables the session helper. You can run the documented manual handoff using the project files and your client without Python.

## Download and install

1. On GitHub, select a published `vX.Y.Z` tag or a specific implementation commit, then choose **Code → Download ZIP**. Branch snapshots can change, so prefer a tag or commit when sharing an installation. Review the extracted installer before running it. [GitHub download instructions](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)
2. Open a shell in the extracted directory that contains `scripts/` and `template/`.
3. Run `./scripts/install.ps1 -Destination 'C:\Projects\my-app'` in PowerShell or `bash scripts/install.sh "$HOME/projects/my-app"` in Bash. Use your actual project path. The final directory can be created if its parent exists.
4. For an existing project, review lines beginning `Kept existing` before starting an agent. Bring over any needed starter rules, setting keys, or template structure by reviewing a diff. Keep existing project decisions and provider configuration.

The installer copies the template's files and hidden directories. It skips local runtime state and does not initialize Git. Windows PowerShell, PowerShell 7, and Git Bash were exercised on Windows. Linux, macOS, and WSL2 Bash are target environments. For the scope of testing, see [Verification](VERIFICATION.md).

## Start Bootstrap

Open the destination in a new session. Select a model and effort from the [model guide](MODELS.md), then send the following prompt.

```text
Read ASK_ME.md and follow its instructions to initialize and configure this project.
```

Answer the short configuration interview. Bootstrap records the project description and constraints, signs off its own setup, and gives Director a narrow handoff. Review any provider configuration changes before trusting project-local settings. Follow the reported Director link or ID if the current client exposes it. Otherwise start a new session from the same project root and paste the handoff prompt Bootstrap provides.

You can use Codex for every role, Claude Code for every role, or assign a provider to each role. For example, use Claude Code to plan and use Codex to execute, then exchange a short handoff and the shared plan through the [communication workflow](../template/docs/COMMUNICATION.md).

## Run one small project task

Tell Director what you want and how you will know it works. Ask it to record deferred ideas in the idea queue. Director can route a clear, scoped request directly and bring in Planner for initial architecture or larger changes. Approve a draft plan through Director before implementation starts. The Orchestrator records work in `tasks/INDEX.md` and reports verified outcomes through Director. Review changes locally and decide when to commit or push.

For local Codex sessions, configure the [automatic TASK and REPORT path](../template/docs/COMMUNICATION.md#automatic-codex-delivery). Start the native daemon for saved idle targets and register the actual Director and Orchestrator thread IDs. On Windows, use the [verified Desktop setup](VERIFICATION.md#live-codex-workflow) with both sessions loaded and able to run the relay helper.

For Claude or mixed sessions, register and verify both roles first, then set the outgoing `TASK` route and return `REPORT` route in their briefs. A loaded Claude session can receive a native peer marker. An external sender can use the opt-in Claude CLI relay if the target is discoverable and you approve the extra subscription turn. [Claude delivery](../template/docs/COMMUNICATION.md#delivery-to-claude-code) · [Mixed-provider handoff](CLAUDE_HANDOFF.md)

## Upgrade a customized installation

Download the new version into a separate directory. Install into a scratch project, compare it with your working installation, and apply the changes you want. Running the installer again can add missing files, and preserves any existing files it encounters. Keep your current plan, task records, memory, and local runtime. Check the changelog and the session helper help before bringing any changed commands into a running project. [Changelog](../CHANGELOG.md)
