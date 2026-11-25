# Session communication

Use native subagents for work that fits inside one parent session. Give longer-lived roles fresh sessions with only their assigned brief and project references. A role, a provider session, a business task and a worktree each have their own identity.

## Open or resume a session

Start a fresh chat in the chosen provider and working directory. Use the role prompt in `docs/roles/` and the provider selection in [MODELS.md](MODELS.md). Ask the session to confirm its role, the project path and its immediate responsibility. Capture its actual native session ID from the provider. A session name, a locally generated UUID or the ID of an in-process worker is insufficient.

Codex can start a persistent CLI thread with `codex exec --json -` and a brief on stdin. The `thread.started` event contains `thread_id`. Add `--skip-git-repo-check` when the project has no Git repository. Set `--sandbox read-only` for an initial confirmation that needs no edits. Open a saved thread with `codex resume UUID` or run a single follow-up with `codex exec resume --json UUID -`. Use only one writer for a saved thread. See [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) and the [CLI reference](https://learn.chatgpt.com/docs/cli/reference).

Claude Code can start with `claude --bg --name Director "Read the Director role and confirm readiness"` and show its actual background ID with `claude agents --json`. Use `claude attach UUID` for its live terminal view. Alternatively, use `claude -p --output-format stream-json --verbose "Read the Director role and confirm readiness"` and capture `session_id` from `system/init` or `result`. Use `claude --resume UUID` to open a saved inactive session. For authorized single-turn follow-up to an inactive session, use `claude -p --resume UUID --output-format json "MESSAGE"`. Confirm the documented authentication and billing behavior for the selected mode before a headless run. See [Claude CLI reference](https://code.claude.com/docs/en/cli-reference), [background sessions](https://code.claude.com/docs/en/agent-view) and [programmatic mode](https://code.claude.com/docs/en/headless).

When starting a headless session, retain its provider output in a private local location only for as long as needed. Observe the process exit code and verify the expected readiness response. If neither automatic creation nor reliable ID capture is available, ask the user to open a new provider chat with the role brief. Record provisioning as pending until you can confirm readiness and see the real ID.

## Provider routing

| Sender → recipient | Native option | Delivery evidence |
|---|---|---|
| Codex → Codex | `python tools/session.py send FILE --wake` submits a wake through `codex queue --resume`. | The helper records the native queue receipt. The target calls `receive` to confirm receipt and deduplicate. |
| Claude → Claude | Use native `ListAgents` and `SendMessage` where available. Select the registered project session. | Use the native delivery result and check that the target receives the message. A one-shot idle notice tracks session activity. |
| Claude → Codex | Invoke the same authorized Codex CLI command from the shell, or use the optional Codex plugin for a scoped task. | Check the Codex target or inspect the plugin job result, according to the mechanism used. |
| Codex → Claude | Relay to Claude in its own UI. A confirmed inactive session can accept the authorized follow-up command above. | Confirm the intended Claude session and the provider result. |

The project relay below works with every pairing, including a single provider. Deliver messages manually when the native route is unavailable, the target session cannot be verified, or a reliable acknowledgement is unavailable. Claude's inbox socket requires authenticated access. The starter uses the documented public mechanisms and retains no messaging tokens. See [Codex developer commands](https://learn.chatgpt.com/docs/developer-commands), [Claude cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging), and the [optional Codex plugin](https://github.com/openai/codex-plugin-cc).

When available, use `codex://threads/THREAD_ID` to open a known Desktop thread and `claude --desktop --resume UUID` to open a supported Claude session. Confirm on the intended machine that the session opens and has the expected history. CLI, background and Desktop sessions can have different visibility or live state. Keep native delivery and opening a session as separate operations. See [Codex Desktop commands](https://learn.chatgpt.com/docs/reference/commands), [Claude Desktop](https://code.claude.com/docs/en/desktop), and the [starter troubleshooting guide](https://github.com/krsticlazar/multi-agent-project-starter/blob/main/guides/TROUBLESHOOTING.md).

## Envelope and relay

Send a short English message when assigning a task, reporting an outcome, surfacing a blocker or consulting a specialist. Use one request ID per delegation or consultation and follow the parent's task ID where applicable. Include task artifacts, verification, blockers and the next required action in `payload`. Keep credentials, raw logs and full transcripts outside the relay.

```json
{
  "message_id": "3bd34f56-4ea9-4560-a3d1-7d34c131da8f",
  "request_id": "REQ-001",
  "task_id": "TASK-001",
  "message_type": "REPORT",
  "sender_role": "development-worker",
  "sender_session_id": "00000000-0000-4000-8000-000000000001",
  "recipient_role": "develop-boss",
  "recipient_session_id": "00000000-0000-4000-8000-000000000002",
  "payload": "Completed. Verification passed. See tasks/TASK-001.md for results and integration notes."
}
```

The UUIDs above illustrate the format. Generate a unique message UUID for each message and use provider-issued UUIDs for actual sessions. Use `null` for `task_id` if the event has no business task, such as a request-level `TASK` sent before an Orchestrator allocates individual tasks. Reuse the request ID in the corresponding report. `REPORT` and `CONSULTATION_RESULT` close the corresponding delegation or consultation. `BLOCKER` and `CONSULTATION` surface an issue or question requiring attention. A turn ending or a transport acknowledging acceptance does not satisfy a business task. An envelope is routing metadata and carries no user approval or authentication.

### Optional Python relay

Use Python 3.10 or newer from the project root. `python` can be `python3` or `py -3` on your machine. The helper uses the standard library and has no provider or network dependency.

```text
python tools/session.py init
python tools/session.py status
python tools/session.py register codex director DIRECTOR_UUID --model CONFIRMED_MODEL
python tools/session.py update DIRECTOR_UUID --status IDLE
python tools/session.py capture claude planner PROVIDER_OUTPUT.jsonl --parent DIRECTOR_UUID
python tools/session.py update PLANNER_UUID --status IDLE
python tools/session.py send MESSAGE.json
python tools/session.py inbox RECIPIENT_UUID
python tools/session.py ack RECIPIENT_UUID MESSAGE_UUID
```

The role arguments follow the lowercase slugs in `session.py register --help` and the role files. Use `register` when you obtained a real ID interactively. An omitted model is recorded as `default` unless the Claude event reports its model. `capture` accepts JSON, JSON Lines or `-` for UTF-8 stdin. It registers a real ID as `STARTING`. Inspect the actual provider response before marking it `IDLE`, even when the turn succeeded. If the provider returned a nonzero exit code, supply `--exit-code CODE` alongside its output.

`send` records a pending envelope. Use `inbox` when an event or supervised handoff calls for delivery. Deliver the pending envelope using the verified native or manual route. Run `ack` only after verifying receipt by the addressed session. `ack` records local delivery without generating an AI response. Reuse the same message ID after an ambiguous failure and check the target before retrying. The registry rejects unknown sessions, mismatched roles and new messages to or from retired sessions. A locally registered UUID does not establish live reachability. Keep a report pending when you cannot establish receipt. When no registered destination exists, preserve the checkpoint and undelivered report under the ignored `.runtime/handoffs/` directory for the primary writer to route. Identical terminal reports for the same request, task and route roles reuse the original record. A conflicting terminal report requires review of the task record.

Use `update UUID --status RUNNING --task TASK-001 --request REQ-001` before starting work. Omit `--task` for a request-level assignment. Update status after checkpointing and use `--clear-task` only after the assignment has been reported or reassigned. Check project pause before dispatch and again before any new work.

The primary checkout contains `.runtime/state.json`. A Git-linked checkout resolves the same primary root. To register a worker in a linked worktree, run the helper from that worktree using its local copy or the primary helper path. Set `--cwd WORKTREE` before the subcommand if the caller is in a different checkout. Runtime writes require access to the primary runtime directory. When the worker sandbox restricts that path, have the authorized primary writer relay the checkpoint. The helper takes an operating-system file lock and atomically replaces state. It refuses a tracked runtime or one it cannot verify is ignored. Git still permits deliberately forced staging, so keep `.runtime/` out of every diff and distribution package. Use a local filesystem with reliable locking and restrict the project directory to trusted local collaborators. Keep project memory and master task state in the primary checkout.

### Automatic Codex delivery

Use two local Codex sessions in the same project and Codex home. The owner can run `codex app-server daemon start` and verify it with `codex app-server daemon version` to allow a saved session to wake. The helper uses the installed `codex` command and the registered target's working directory. Before dispatch, verify that each target can run `python tools/session.py status` with the session's normal workspace permissions. Receipt requires writing the local runtime. A session provisioned for a read-only readiness check needs workspace access before it can consume the relay.

1. Start and verify independent Director and Orchestrator sessions, then register their actual Codex thread UUIDs and mark them `IDLE`. Open a saved session in Desktop with `codex://threads/THREAD_ID` where supported.
2. Director writes a `TASK` envelope with a new message UUID, the authorized request ID, `task_id` set to `null`, and the two actual session UUIDs. Orchestrator sends a `REPORT` with the same request ID and the actual task ID, or `null` for a request-level report. Use `python tools/session.py send FILE --wake` for either envelope and end the sending turn after checking the result.
3. The helper first persists the envelope and reserves one submission. It sends a short native wake containing the target and message UUIDs. The destination invokes `python tools/session.py receive RECIPIENT_UUID MESSAGE_UUID` from the project root. This atomically returns and acknowledges the addressed envelope once. A duplicate wake returns `null`. The destination checks authorization in the approved records before work. Director presents the terminal report in the user's language and ends its turn.

`QUEUED` records native acceptance. `QUEUED_RESUME_WARNING` records acceptance plus a failed resume attempt. An already-loaded Desktop session may still pick up the item from the shared queue. The local `delivered_at` field is set by `receive` or explicit manual acknowledgement. It records receipt of the business envelope. Verify the corresponding task artifact or visible Director response for completion.

`NOT_ATTEMPTED` leaves the envelope pending. Resolve the stated reason and reuse the same envelope if an automatic attempt is still appropriate. `SUBMITTING` after an interrupted process and `UNKNOWN` mean that the native result could be ambiguous. Inspect the session history and `.runtime/state.json` before recovery. Keep the original message ID, use `receive` in the confirmed destination when necessary, and check its task record if receipt already happened. A repeat `send --wake` returns the stored attempt after submission, even if the caller uses a new UUID for an identical terminal report. Native queue submission is at most once per project envelope. A native alert or a transport receipt alone is insufficient evidence that an agent finished a business task. [Codex queue reference](https://learn.chatgpt.com/docs/developer-commands)

### Manual relay without Python

Use the native provider's session list and a single designated writer for the local session roster, pause state and pending reports in the primary `.runtime/` directory. Before recording anything in a Git project, verify that `git ls-files -- .runtime` returns no tracked entries. Add `.runtime/` to Git's local ignore rules or create `.runtime/.gitignore` containing `*`, then verify that `git check-ignore .runtime/STATE.md .runtime/handoffs/example.json` lists both paths. Use `.runtime/STATE.md` for the roster and pause and `.runtime/handoffs/` for pending envelopes. Store each envelope under its unique message ID. Check for an existing copy before retrying and record delivery after verifying receipt. Tell the parent when a checkpoint is ready through the next available session turn or user relay. Avoid polling and model-generated acknowledgements.

## Callbacks and coordinated pause

An explicit `REPORT` captures the business outcome. After an observed provider failure, run `observe` with the structured result or a confirmed process exit code. For example, use `python tools/session.py observe UUID PROVIDER_OUTPUT.jsonl --exit-code 1`. Use output from the registered session only. The helper recognizes Codex CLI `turn.failed`, Codex App Server failed `turn/completed`, Claude Code failed `result` and Claude `StopFailure`. It stores a short deduplicated `BLOCKER` addressed to the registered parent, when one exists. A trusted project-local hook or client can pass the event to `python tools/session.py observe auto -` if its JSON includes one supported native session ID. Call the helper with the actual registered UUID when the output lacks the session ID. No hooks are enabled by default. See [Codex App Server notifications](https://learn.chatgpt.com/docs/app-server), [Codex hooks](https://learn.chatgpt.com/docs/hooks) and [Claude hooks](https://code.claude.com/docs/en/hooks).

For an authorized continuation of a registered, inactive Codex session, run this PowerShell example from the project root. The failure path records a local event without starting a follow-up model turn.

```powershell
$sessionId = 'REGISTERED_UUID'
$eventFile = New-TemporaryFile
$recorded = $false
try {
    codex exec resume --json $sessionId 'Continue the authorized assignment.' |
        Set-Content -LiteralPath $eventFile.FullName -Encoding utf8 -ErrorAction Stop
    $providerExit = $LASTEXITCODE
    if ($providerExit -ne 0) {
        python tools/session.py observe $sessionId $eventFile.FullName --exit-code $providerExit
        if ($LASTEXITCODE -ne 0) { throw "Callback failed. Private event file retained at $($eventFile.FullName)" }
    } else {
        Get-Content -LiteralPath $eventFile.FullName
    }
    $recorded = $true
} finally {
    if ($recorded) { Remove-Item -LiteralPath $eventFile.FullName }
}
```

A failed Codex App Server turn with `usageLimitExceeded` triggers the shared pause. Claude `rate_limit`, CLI error text and process exit status require provider confirmation of subscription quota exhaustion. Once confirmed, use `python tools/session.py pause UUID --reason "Subscription usage limit confirmed"` and optionally `--reset-at` with the provider's known timestamp. The helper records the rate-limited session, stores the pause and blocks new `TASK` dispatch and `RUNNING` transitions. Without Python, the designated writer records the equivalent pause and pending notification in `.runtime/STATE.md`.

Reach a safe checkpoint for work already running and preserve unfinished changes. Report through the Director when available. Keep any undelivered report locally. This cooperative pause depends on agents checking it at task boundaries. It cannot interrupt active provider turns. There is no automatic provider switch or paid fallback. After explicit user approval, run `python tools/session.py resume --user-approved` or clear the manual pause. Verify provider availability and mark the ready sessions `IDLE` before restarting their work.

## Rotation

Use native compaction first. When replacing a session, checkpoint and park the old session, start a fresh chat and verify its actual ID and brief. Register the replacement with the same role and mark it `IDLE`. Run `python tools/session.py rotate OLD_UUID NEW_UUID` to retire the old record and move its current assignment, child routing and pending inbound envelopes in one update. Confirm native turns are quiescent before handing off. The helper cannot stop an old provider session or move a message it already accepted. Inspect that target before redelivery. For manual rotation, the roster writer performs these same changes at one handoff and keeps the older ID for history.
