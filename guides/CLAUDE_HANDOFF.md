# Claude Code and mixed-provider handoff

This phase adds local Claude and mixed-provider routes to the existing Session Registry. The [communication guide](../template/docs/COMMUNICATION.md) describes provisioning, permissions, routing, and recovery. [Verification](VERIFICATION.md) records the Windows CLI transport check and the earlier Codex Desktop result.

## Prepare the project

1. Start the Director and Orchestrator in the project with their chosen providers and role briefs. Use normal permissions. Confirm each role can read and write the shared relay and record its actual UUID, working directory, parent route, and readiness. Keep one writer per provider session.
2. Choose a route in each direction. Use `send FILE --wake` for a Codex target. For native Claude peers, use the reserved trigger with `SendMessage`. For a loaded, uniquely named Claude target reachable from the CLI, the owner can opt into `send FILE --wake --claude-relay PEER_NAME`. Record both choices in the role briefs before dispatch. The CLI relay uses an extra Claude subscription turn per wake.
3. On Windows, load the Codex targets in Desktop if the separate native daemon cannot provision workspace execution. For Claude, confirm that the intended surface can see and address the target. When opening a saved CLI conversation in Claude Desktop, first close its previous writer. A missing peer or an unavailable permission leaves a recoverable local envelope.
4. If using Claude's optional `StopFailure` hook, install it from the communication guide and verify that Claude can launch Python. Confirm a subscription limit in the provider before setting the coordinated pause. Resume after user approval.

## First real project check

Use an approved project request after reviewing and approving an implementation checkpoint. The project owner conducts this check.

- Confirm the Director's `TASK` is persisted before the target wakes. Note native acceptance and verify that the Orchestrator receives the exact addressed envelope once.
- Confirm the Orchestrator checkpoints its results, sends one `REPORT`, and the Director presents it in the expected conversation without an additional user prompt when both routes support delivery.
- Verify that the expected history is visible in the selected Desktop app. Check the local envelope and task record before recovering an uncertain delivery. Use the original message UUID and verify the intended recipient before resuming or rotating.

The local Claude CLI smoke established discovery, inbox acceptance, and an idle target turn. Live Claude → Codex shell dispatch, busy Claude peers, the mixed project round trip, and Claude Desktop roster visibility remain acceptance checks. The public Claude inbox docs describe Windows authentication without a stable external message submission and acknowledgement contract. The project uses the official CLI and native tools for the opt-in route. [Claude peer messaging](https://code.claude.com/docs/en/cross-session-messaging) · [Claude Code Desktop](https://code.claude.com/docs/en/desktop#coming-from-the-cli)
