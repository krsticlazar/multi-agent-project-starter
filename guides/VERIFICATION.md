# Verification and platform status

Last checked on 2026-11-25. In a new environment, verify native feature availability with the installed provider and the selected account.

## Native transport results

| Route | Evidence | Operating path |
| --- | --- | --- |
| Codex → Codex | On native Windows, Codex CLI 0.172.0 created a saved session under ChatGPT authentication. JSONL supplied a real thread ID. The queue accepted a message and returned exit 0 while warning that it could not wake the session without a local daemon. Explicit resume consumed the queued message and produced a response in the same history. | Use native queue for an eligible target and verify consumption separately. Resume a stopped session explicitly when automatic wake is unavailable. |
| Claude Code → Claude Code | CLI 2.1.332 was installed and signed out. Live discovery, delivery, and idle notification remain open. | In an authenticated installation that supports local peers, use `ListAgents` and `SendMessage`. Otherwise relay the saved project message. |
| Claude Code → Codex | Codex queue was exercised from a local shell. Calling it from a Claude Code turn and receiving a report there remain open. | An authenticated Claude Code session with the necessary shell permission can use the Codex command. Keep the return report in the project relay until received. |
| Codex → Claude Code | The Claude inbox documentation covers discovery, inbound control, and authentication for the local socket. The reviewed public docs do not specify a stable external message payload and confirmation contract. | Use the project relay or explicitly resume a stopped Claude session through its supported CLI. |

The Codex stdio App Server also completed its initialization handshake and returned `gpt-6.2-sol` and `gpt-6.2-astra` with `low` through `ultra` reasoning, and `gpt-6-luna` through `max`, in the test account's model catalog. Claude model and effort availability can be checked after sign-in. The starter keeps the provider's credentials in its official client. [Codex CLI](https://learn.chatgpt.com/docs/cli/reference) · [Codex App Server](https://learn.chatgpt.com/docs/app-server) · [Claude Code messaging](https://code.claude.com/docs/en/cross-session-messaging) · [Claude Code CLI](https://code.claude.com/docs/en/cli-reference)

## Desktop

- **Opened on Windows.** The documented Codex `codex://threads/<id>` link opened the exact headless smoke-test session in the desktop app. The conversation included the creation turn, externally queued input consumed at resume, and the resumed response. The test thread did not appear in the first 50 app history entries before explicitly opening it. Automatic sidebar listing, TUI handoff, daemon-managed background visibility, live refresh, and simultaneous writer handling remain open. [Codex Desktop commands](https://learn.chatgpt.com/docs/reference/commands)
- **Claude Code desktop.** The Windows app was present and Claude Code CLI was signed out. Native documentation describes `/desktop` or `claude --desktop --resume <id>` for local subscription-backed sessions on macOS and x64 Windows. CLI and Desktop keep separate session lists. End the CLI or background writer before opening the same session in Desktop. Actual transcript, sidebar, external messages, and live progress remain open in this environment. [Claude Code Desktop](https://code.claude.com/docs/en/desktop)

## Retest with an authenticated account

Use a disposable project and harmless one-line messages. Create two local sessions, check the IDs and project scope, and send one message to a waiting session. Confirm it is consumed and produces a return report. Repeat with an active turn and record whether the provider queues, refuses, or injects the message. Open the session in Desktop by its supported mechanism and check the actual transcript, sidebar, and live progress. Keep one writer per session. Test quota handling with the runtime's synthetic-event checks.

## Repository checks

Run `python -B -m unittest discover -s tests -v` for archive installation and collision cases, local relay delivery and session rotation, concurrent state updates, synthetic quota callbacks, and uncommitted worktree integration. The suite checks failure paths without spending a subscription quota. It exercises the installers available on the host.

The installed payload and ZIP installation were tested with Windows PowerShell 5.1, PowerShell 7.6.9, and Git Bash 5.3.15 on native Windows. Linux, macOS, and a separate WSL2 user distribution are target environments awaiting local tests. Codex project guidance and the checkpoint skill were detected through the native client. Claude Code validated the project agent and skill definitions locally without sign-in.

## Live Codex workflow

A disposable non-Git Windows project completed a guided installation-to-report run with live Codex agents under ChatGPT authentication. Bootstrap personalized the installed project and initialized local runtime. A clean CLI Director returned its actual thread ID and a Planner handoff. The helper captured that ID. A native Planner drafted revision 1. The fixture owner approved it and authorized execution through the Director. A separate native Orchestrator delegated to one nested development worker, verified the exact 16-byte greeting, and updated the task index, memory, and execution checklist. The test driver queued the Orchestrator's report and explicitly resumed the Director, which delivered the final summary.

The test driver relayed role handoffs and recorded the approval. A standalone headless CLI Bootstrap attempt hit the Windows runtime's filesystem policy before it could read its instructions. Bootstrap succeeded through the Codex harness with workspace access. The test establishes the guided workflow and the observed Codex CLI delivery path. Hands-off provisioning, active-target messaging, and an authenticated Claude or mixed-provider workflow remain open.

For the project workflow, use the [getting-started guide](GETTING_STARTED.md) and the [relay procedure](../template/docs/COMMUNICATION.md).
