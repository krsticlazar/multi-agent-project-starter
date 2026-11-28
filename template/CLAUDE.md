@AGENTS.md

## Claude Code

Use the project agents under `.claude/agents/` for explicitly assigned roles. Shared role instructions live under `docs/roles/`. Read the role briefing directly if the agent picker is unavailable.

Installed plugins, skills and MCP servers from `docs/PLUGINS.md` are used through Claude Code's native skill and MCP tools. Native subagents may not have every tool of the parent session, so name the add-on in the subagent prompt and let it report when the tool is missing.

Use the [communication guide](docs/COMMUNICATION.md) to register the UUID shown by `/status` and route cross-session messages. If native `SendMessage` is available, match the peer to the registered UUID and project before sending a saved relay marker. Keep the session's native inbound and permission controls in force. For an incoming marker, verify the recipient UUID against your registration and follow your role's receipt procedure using the message UUID.

## Agent skills

### Issue tracker

Issues live in GitHub Issues, used through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
