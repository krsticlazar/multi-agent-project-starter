@AGENTS.md

## Claude Code

Use the project agents under `.claude/agents/` for explicitly assigned roles. Shared role instructions live under `docs/roles/`. Read the role briefing directly if the agent picker is unavailable.

Use the [communication guide](docs/COMMUNICATION.md) to register the UUID shown by `/status` and route cross-session messages. If native `SendMessage` is available, match the peer to the registered UUID and project before sending a saved relay marker. Keep the session's native inbound and permission controls in force. For an incoming marker, verify the recipient UUID against your registration and follow your role's receipt procedure using the message UUID.
