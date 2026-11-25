# Claude Code integration handoff

Claude and mixed-provider live work is deferred until an authenticated Claude Code environment is available. This guide records the current interface and the remaining acceptance checks. Consult [verification](VERIFICATION.md) for observed results and [session communication](../template/docs/COMMUNICATION.md) for the operating procedure.

## Existing components

- The [Claude project directory](../template/.claude/) contains native agent definitions, settings, and a checkpoint skill adapter. [CLAUDE.md](../template/CLAUDE.md) imports the common agent rules. The project models guide describes how Bootstrap records provider and model choices.
- The [session helper](../template/tools/session.py) maintains the Session Registry and relay in the primary checkout's ignored `.runtime/state.json`. Register interactive UUIDs with `register`, or use `capture claude ROLE FILE` with provider JSON or JSONL from `system/init` or `result`. Verify readiness before setting the registry status to `IDLE`. Keep provider IDs and work directories local.
- `send FILE` persists a provider-independent envelope for a registered route. `inbox` reads pending messages. `receive RECIPIENT_UUID MESSAGE_UUID` acknowledges and returns the addressed envelope once. `ack` records verified manual delivery. Use `rotate` after checkpointing to transfer routing and pending envelopes. State updates use a file lock and an atomic replacement.
- `observe` accepts a CLI outcome, a structured callback, or a native event with `observe auto -` if it exposes a supported session ID. It records qualifying failures and queues a local `BLOCKER`. The Claude parser handles failed `result` and `StopFailure`; a rate-limit indication needs subscription-specific confirmation before setting the shared pause. The helper includes no enabled hook of its own.
- Automatic Codex routing uses an explicit `send FILE --wake` after a role checkpoints its `TASK` or `REPORT`. `codex queue --resume` receives a marker with the local message UUID. The destination calls `receive`. The persisted submission attempt prevents duplicate native sends. Queue acceptance, envelope receipt, and task completion each have their own evidence.

The Windows smoke verified the full Codex-only request and report round trip with both sessions loaded in Desktop and able to run the helper. A separate native daemon can wake a saved session. In the tested environment its background shell lacked workspace provisioning, so the helper preserved the pending task for recovery.

## Work to resume

1. Sign in through the official Claude client. Verify its version, availability of local peer messaging, background session capture, and eligible Desktop opening paths with small disposable chats.
2. Verify Claude → Claude with local peer discovery and `SendMessage`, including idle activation, busy behavior, inbound controls, and one terminal report. Test Claude → Codex by calling the native Codex transport within an authorized Claude session and validating actual receipt.
3. Verify Codex → Claude with a supported Claude-owned target or an explicitly inactive saved session. Keep the provider-neutral relay for recovery. Choose any additional automation only after verifying published transport, authentication, ownership, and delivery behavior on Windows.
4. Run a mixed-provider Director and Orchestrator fixture. Confirm which Desktop client displays each turn, the live return report, duplicate suppression, and the shared pause. Preserve native permission settings and session ownership throughout.

Keep credentials with their provider. The registry stores local routing and delivery evidence. For a newer provider adapter, preserve the existing envelope, retry discipline, and receipt semantics before extending the transport.
