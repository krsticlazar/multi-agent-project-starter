#!/usr/bin/env python3
"""Manage the starter's local registry, pause state and message relay."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile
from uuid import NAMESPACE_URL, UUID, uuid5


PROVIDERS = ("codex", "claude")
PEER_RESULTS = ("ACCEPTED", "HELD", "REFUSED", "UNKNOWN")
ROLES = (
    "bootstrap", "director", "planner", "orchestrator", "supervisor",
    "research-boss", "develop-boss", "review-boss", "research-worker",
    "development-worker", "review-worker", "subagent",
)
STATUSES = ("STARTING", "IDLE", "RUNNING", "BLOCKED", "COMPLETED", "FAILED", "RATE_LIMITED", "RETIRED")
MESSAGE_TYPES = ("TASK", "REPORT", "BLOCKER", "CONSULTATION", "CONSULTATION_RESULT")
ENVELOPE_FIELDS = {
    "message_id", "request_id", "task_id", "message_type", "sender_role",
    "sender_session_id", "recipient_role", "recipient_session_id", "payload",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def session_id(value):
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        raise ValueError("Expected a native session UUID.") from None


def task_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"TASK-[0-9]{3,}", value):
        raise ValueError("Expected a task ID like TASK-001.")
    return value


def input_text(source):
    if source == "-":
        return sys.stdin.buffer.read().decode("utf-8-sig")
    return Path(source).read_text(encoding="utf-8-sig")


def git(directory, *args):
    return subprocess.run(["git", "-C", str(directory), *args], capture_output=True, check=False)


def project_paths(installation):
    has_git = any((parent / ".git").exists() for parent in (installation, *installation.parents))
    if not shutil.which("git"):
        if has_git:
            raise ValueError("Git must be available to protect runtime state in a Git project.")
        return [installation], False

    prefix = git(installation, "rev-parse", "--show-prefix")
    if prefix.returncode:
        if has_git:
            raise ValueError("Cannot resolve the Git project for this installation.")
        return [installation], False

    worktrees = git(installation, "worktree", "list", "--porcelain", "-z")
    if worktrees.returncode:
        raise ValueError("Cannot resolve linked Git worktrees.")
    records = worktrees.stdout.split(b"\0")
    if b"bare" in records:
        raise ValueError("The runtime requires a primary Git working tree.")
    relative_path = Path(os.fsdecode(prefix.stdout.removesuffix(b"\n")))
    roots = [
        (Path(os.fsdecode(record.removeprefix(b"worktree "))) / relative_path).resolve()
        for record in records if record.startswith(b"worktree ")
    ]
    if not roots or not roots[0].is_dir() or installation not in roots:
        raise ValueError("Cannot locate the primary project installation.")
    return roots, True


def runtime_directory(root, in_git):
    runtime = root / ".runtime"
    if runtime.resolve() != runtime:
        raise ValueError("The runtime directory must be inside the primary project.")
    if in_git:
        tracked = git(root, "ls-files", "-z", "--", ".runtime")
        if tracked.returncode or tracked.stdout:
            raise ValueError("Cannot use a runtime directory with tracked files.")

    runtime.mkdir(mode=0o700, exist_ok=True)
    for name in (".gitignore", "state.json", ".state.lock"):
        path = runtime / name
        if path.resolve() != path:
            raise ValueError(f"Runtime path {name} must be a local file.")
    return runtime


def protect_runtime(runtime, in_git):
    try:
        with (runtime / ".gitignore").open("x", encoding="ascii") as ignore_file:
            ignore_file.write("*\n")
    except FileExistsError:
        pass

    if in_git:
        for name in (".gitignore", "state.json", ".state.lock", ".state-example.tmp"):
            ignored = git(runtime.parent, "check-ignore", "--no-index", "-q", "--", f".runtime/{name}")
            if ignored.returncode:
                raise ValueError(f"Exclude .runtime/ from Git before using it. {name} is not ignored.")

@contextmanager
def state_lock(runtime):
    with (runtime / ".state.lock").open("a+b") as lock_file:
        lock_file.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield


def write_state(runtime, state):
    stream = NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=runtime, prefix=".state-", suffix=".tmp", delete=False,
    )
    temporary = Path(stream.name)
    try:
        with stream:
            json.dump(state, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, runtime / "state.json")
    finally:
        temporary.unlink(missing_ok=True)


def read_state(runtime):
    path = runtime / "state.json"
    if not path.exists():
        return {"version": 1, "pause": None, "sessions": {}, "messages": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state["version"] != 1:
        raise ValueError("Unsupported runtime state version.")
    return state


def registered(state, value):
    value = session_id(value)
    if value not in state["sessions"]:
        raise ValueError(f"Session {value} is not registered in this project.")
    return state["sessions"][value]


def register(state, args, cwd, native_id, model=None):
    native_id = session_id(native_id)
    sessions = state["sessions"]
    parent = registered(state, args.parent)["session_id"] if args.parent else None
    if native_id == parent:
        raise ValueError("A session cannot be its own parent.")
    if native_id in sessions:
        existing = sessions[native_id]
        if (existing["agent_role"], existing["provider"], existing["working_directory"]) != (
            args.role, args.provider, str(cwd),
        ):
            raise ValueError("This session ID is already registered with different routing information.")
        return existing
    sessions[native_id] = {
        "agent_role": args.role, "provider": args.provider,
        "model": args.model or model or "default", "session_id": native_id,
        "parent_session_id": parent, "status": "STARTING",
        "current_task_id": None, "request_id": None, "working_directory": str(cwd),
        "created_at": now(), "updated_at": now(),
    }
    return sessions[native_id]


def events(source, allow_empty=False):
    contents = input_text(source)
    if not contents.strip() and allow_empty:
        return []
    try:
        records = [json.loads(contents)]
    except json.JSONDecodeError:
        records = [json.loads(line) for line in contents.splitlines() if line.strip()]
    if not records or any(not isinstance(record, dict) for record in records):
        raise ValueError("Expected native JSON or JSON Lines event output.")
    return records


def event_session(provider, event):
    if provider == "codex":
        if event.get("type") == "thread.started":
            return event["thread_id"]
        if event.get("method") == "turn/completed":
            return event["params"]["threadId"]
    if provider == "claude":
        if event.get("type") == "result" or (
            event.get("type") == "system" and event.get("subtype") == "init"
        ) or event.get("hook_event_name") == "StopFailure":
            return event.get("session_id")
    return None


def envelope_key(envelope):
    return tuple(envelope[key] for key in (
        "message_type", "request_id", "task_id", "sender_role", "recipient_role",
    ))


def queue(state, envelope):
    if not isinstance(envelope, dict) or set(envelope) != ENVELOPE_FIELDS:
        raise ValueError("The message must contain exactly the documented envelope fields.")
    envelope["message_id"] = session_id(envelope["message_id"])
    if not isinstance(envelope["request_id"], str) or not envelope["request_id"].strip():
        raise ValueError("A message requires a request ID.")
    if envelope["task_id"] is not None:
        task_id(envelope["task_id"])
    if envelope["message_type"] not in MESSAGE_TYPES:
        raise ValueError("Unknown message type.")
    if not isinstance(envelope["payload"], str) or not envelope["payload"].strip():
        raise ValueError("The message payload must be a nonempty plain-text summary.")
    for side in ("sender", "recipient"):
        route = registered(state, envelope[f"{side}_session_id"])
        if route["agent_role"] != envelope[f"{side}_role"]:
            raise ValueError(f"The {side} role does not match its registered session.")
        envelope[f"{side}_session_id"] = route["session_id"]
    messages = state["messages"]
    message_id = envelope["message_id"]
    previous = messages.get(message_id)
    if previous:
        routed = dict(previous["envelope"], recipient_session_id=previous["recipient_session_id"])
        if envelope not in (previous["envelope"], routed):
            raise ValueError("This message ID already belongs to a different envelope.")
        return previous
    if envelope["message_type"] in ("REPORT", "CONSULTATION_RESULT"):
        for previous in messages.values():
            if envelope_key(previous["envelope"]) == envelope_key(envelope):
                if previous["envelope"]["payload"] != envelope["payload"]:
                    raise ValueError("A different terminal report already exists for this request and task.")
                return previous
    sender = registered(state, envelope["sender_session_id"])
    recipient = registered(state, envelope["recipient_session_id"])
    if sender["status"] == "RETIRED" or recipient["status"] == "RETIRED":
        raise ValueError("Refresh the routing before sending to or from a retired session.")
    if envelope["message_type"] == "TASK" and state["pause"]:
        raise ValueError("Development is paused. A new TASK cannot be queued.")
    messages[message_id] = {
        "envelope": envelope, "recipient_session_id": recipient["session_id"],
        "queued_at": now(), "delivered_at": None,
    }
    return messages[message_id]


def prepare_wake(state, message, relay_name):
    if message["delivered_at"] or any(
        message.get(key, {}).get("status", "NOT_ATTEMPTED") != "NOT_ATTEMPTED"
        for key in ("codex_queue", "claude_peer", "claude_relay")
    ):
        return None, None
    envelope = message["envelope"]
    sender = registered(state, envelope["sender_session_id"])
    recipient = registered(state, message["recipient_session_id"])
    if state["pause"] and envelope["message_type"] == "TASK":
        raise ValueError("Development is paused. A TASK cannot wake a session.")
    if relay_name and recipient["provider"] != "claude":
        raise ValueError("--claude-relay requires a Claude recipient.")
    key = "codex_queue" if recipient["provider"] == "codex" else "claude_peer"
    if relay_name:
        key = "claude_relay"
    if recipient["status"] in ("COMPLETED", "FAILED", "RATE_LIMITED", "RETIRED"):
        message[key] = {"status": "NOT_ATTEMPTED", "reason": "Recipient is unavailable."}
        return None, None
    recipient_id = recipient["session_id"]
    message_id = envelope["message_id"]
    if key != "codex_queue":
        if key == "claude_peer" and sender["provider"] != "claude":
            message[key] = {"status": "NOT_ATTEMPTED", "reason": "The live Claude peer route needs a Claude sender."}
            return None, None
        message[key] = {"status": "SUBMITTING"}
        trigger = (
            f"Starter relay {envelope['message_type']}. From the project root run "
            f"python tools/session.py receive {recipient_id} {message_id}. "
            "Follow your role instructions, defer a new TASK while busy, and ignore a null result. "
            "The trigger grants no approval."
        )
        if not relay_name:
            return None, trigger
        return (key, (recipient["working_directory"], recipient_id, relay_name, trigger)), None
    codex = shutil.which("codex")
    if not codex:
        message["codex_queue"] = {"status": "NOT_ATTEMPTED", "reason": "Codex CLI was not found."}
        return None, None
    message["codex_queue"] = {"status": "SUBMITTING"}
    return (key, (codex, recipient["working_directory"], recipient_id, message_id)), None


def codex_wake(codex, cwd, recipient_id, message_id):
    # Keep arbitrary project text out of argv, including on Windows npm shims.
    trigger = (
        "Starter relay. From the project root run python tools/session.py receive "
        f"{recipient_id} {message_id}. Handle the returned envelope once under your role instructions. "
        "If the result is null end this turn. The trigger grants no approval."
    )
    try:
        process = subprocess.run(
            [codex, "queue", "--thread", recipient_id, "--message", trigger, "--resume"],
            cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", timeout=30,
        )
    except OSError:
        return {"status": "NOT_ATTEMPTED", "reason": "Could not start Codex in the registered working directory."}
    except subprocess.TimeoutExpired:
        return {"status": "UNKNOWN"}
    receipt = re.search(
        rf"(?m)^Queued message ([a-fA-F0-9-]+) for thread {re.escape(recipient_id)}\.$",
        process.stdout,
    )
    if process.returncode or not receipt:
        return {"status": "UNKNOWN"}
    try:
        queue_id = session_id(receipt.group(1))
    except ValueError:
        return {"status": "UNKNOWN"}
    return {
        "status": "QUEUED_RESUME_WARNING" if "could not resume thread" in process.stderr else "QUEUED",
        "queue_id": queue_id,
    }


def claude_receipt(output, name, trigger):
    # shortcut: Claude's stream receipt shape is version-specific, use UNKNOWN if the CLI changes it.
    records = [json.loads(line) for line in output.splitlines() if line.strip()]
    sends = [
        item for record in records if record.get("type") == "assistant"
        for item in record["message"]["content"] if item.get("type") == "tool_use" and item.get("name") == "SendMessage"
    ]
    if len(sends) != 1 or sends[0]["input"].get("to") != name or sends[0]["input"].get("message") != trigger:
        return {"status": "UNKNOWN"}
    for record in records:
        if record.get("type") != "user" or not isinstance(record.get("tool_use_result"), dict):
            continue
        result = record["tool_use_result"]
        if result.get("success") is True and f" → {name} (another Claude session on this machine;" in result.get("message", ""):
            if any(item.get("tool_use_id") == sends[0]["id"] and item.get("is_error") is not True
                   for item in record["message"]["content"] if item.get("type") == "tool_result"):
                return {"status": "QUEUED", "queue_id": session_id(result["msg_id"])}
    return {"status": "UNKNOWN"}


def claude_relay_wake(cwd, recipient_id, name, trigger):
    claude = shutil.which("claude")
    if not claude or (os.name == "nt" and Path(claude).suffix.lower() != ".exe"):
        return {"status": "NOT_ATTEMPTED", "reason": "The native Claude CLI executable was not found."}
    overrides = (
        "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_PROFILE",
        "ANTHROPIC_FEDERATION_RULE_ID", "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_USE_ANTHROPIC_AWS",
        "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
    )
    if any(os.environ.get(key) for key in overrides):
        return {"status": "NOT_ATTEMPTED", "reason": "A Claude authentication or endpoint override is set."}

    def invoke(*args, timeout=10):
        return subprocess.run(
            [claude, *args], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )

    try:
        auth = invoke("--safe-mode", "auth", "status", "--json")
        account = json.loads(auth.stdout)
        if (auth.returncode or account.get("loggedIn") is not True or account.get("authMethod") != "claude.ai"
                or account.get("apiProvider") != "firstParty" or not account.get("subscriptionType")):
            return {"status": "NOT_ATTEMPTED", "reason": "An active Claude subscription login is required."}
        roster = invoke("--safe-mode", "agents", "--json", "--all")
        matches = [
            entry for entry in json.loads(roster.stdout) if entry.get("pid")
            and (entry.get("name") or "").casefold() == name.casefold()
        ]
        if (roster.returncode or len(matches) != 1 or matches[0].get("name") != name
                or matches[0].get("sessionId") != recipient_id
                or Path(matches[0]["cwd"]).resolve() != Path(cwd).resolve()):
            return {"status": "NOT_ATTEMPTED", "reason": "No unique live Claude peer matches the registered route."}
    except (OSError, subprocess.TimeoutExpired, AttributeError, ValueError, KeyError, TypeError):
        return {"status": "NOT_ATTEMPTED", "reason": "Could not verify Claude login and live peer discovery."}

    prompt = (
        f"Use ListAgents to verify exactly one local Claude session named {name}. If absent or ambiguous, stop. "
        f"Then use SendMessage exactly once to {name} with just the following single line verbatim. "
        f"Do not send to any other target or retry. After the tool returns, end the turn.\n{trigger}"
    )
    try:
        process = invoke(
            "-p", "--safe-mode", "--strict-mcp-config", "--model", "haiku",
            "--tools", "ListAgents,SendMessage", "--output-format", "stream-json", "--verbose", "--", prompt,
            timeout=60,
        )
        if process.returncode == 0:
            return claude_receipt(process.stdout, name, trigger)
    except (OSError, subprocess.TimeoutExpired, AttributeError, ValueError, KeyError, TypeError):
        pass
    return {"status": "UNKNOWN"}


def set_pause(state, session, reason, reset_at=None):
    evidence = {
        "session_id": session["session_id"], "provider": session["provider"],
        "reason": reason, "reset_at": reset_at, "paused_at": now(),
    }
    session.update(status="RATE_LIMITED", usage_limit=evidence, updated_at=now())
    if state["pause"] is None:
        state["pause"] = evidence
    return state["pause"]


def notify_parent(state, session, reason):
    parent_id = session["parent_session_id"]
    if not parent_id:
        return
    parent = registered(state, parent_id)
    request_id = session["request_id"] or f"session-{session['session_id']}"
    failure_id = uuid5(NAMESPACE_URL, repr((
        request_id, session["session_id"], session["current_task_id"], reason,
    )))
    queue(state, {
        "message_id": str(failure_id), "request_id": request_id,
        "task_id": session["current_task_id"], "message_type": "BLOCKER",
        "sender_role": session["agent_role"], "sender_session_id": session["session_id"],
        "recipient_role": parent["agent_role"], "recipient_session_id": parent_id,
        "payload": f"Session needs attention. {reason} Review its checkpoint and provider status.",
    })


def observe(state, session, records, exit_code=None):
    if session["status"] in ("COMPLETED", "RETIRED"):
        raise ValueError("Cannot apply a callback to a completed or retired session.")
    provider = session["provider"]
    for record in records:
        observed_id = event_session(provider, record)
        if observed_id and session_id(observed_id) != session["session_id"]:
            raise ValueError("The provider event belongs to a different session.")

    reason = None
    for record in records:
        if provider == "codex" and record.get("method") == "turn/completed":
            turn = record["params"]["turn"]
            if turn.get("status") != "failed":
                continue
            error_info = (turn.get("error") or {}).get("codexErrorInfo")
            if error_info == "usageLimitExceeded":
                reason = "Codex reported usageLimitExceeded."
                set_pause(state, session, reason)
                notify_parent(state, session, reason)
                return session
            reason = "A Codex App Server turn failed."
        elif provider == "codex" and record.get("type") == "turn.failed":
            reason = "A Codex CLI turn failed."
        elif provider == "claude" and (
            record.get("hook_event_name") == "StopFailure"
            or (record.get("type") == "result" and record.get("is_error") is True)
        ):
            reason = "A Claude Code turn failed."

    if exit_code and reason is None:
        reason = f"The provider CLI exited with code {exit_code}."
    if reason and session["status"] != "RATE_LIMITED":
        session.update(status="FAILED", updated_at=now())
        notify_parent(state, session, reason)
    return session


def rotate(state, old, new):
    if old is new or old["agent_role"] != new["agent_role"]:
        raise ValueError("Rotation requires two sessions for the same role.")
    if old["status"] in ("RUNNING", "RETIRED") or new["status"] != "IDLE" or new["current_task_id"]:
        raise ValueError("Checkpoint the old session and verify the idle replacement before rotation.")
    if state["pause"] and old["provider"] != new["provider"]:
        raise ValueError("Resolve the project pause before switching providers.")
    if new["parent_session_id"] not in (None, old["session_id"], old["parent_session_id"]):
        raise ValueError("The replacement must keep the same parent session.")
    old.update(status="RETIRED", updated_at=now())
    new.update(
        parent_session_id=old["parent_session_id"], current_task_id=old["current_task_id"],
        request_id=old["request_id"], updated_at=now(),
    )
    for session in state["sessions"].values():
        if session["parent_session_id"] == old["session_id"]:
            session.update(parent_session_id=new["session_id"], updated_at=now())
    for message in state["messages"].values():
        if not message["delivered_at"] and message["recipient_session_id"] == old["session_id"]:
            message["recipient_session_id"] = new["session_id"]
    return new


def run(state, args, cwd, data):
    action = args.action
    if action in ("init", "status"):
        return {
            "pause": state["pause"], "sessions": state["sessions"],
            "pending_messages": sum(not message["delivered_at"] for message in state["messages"].values()),
        }
    if action == "send":
        return queue(state, data)
    if action == "peer-result":
        message = state["messages"].get(session_id(args.message_id))
        if not message or message["envelope"]["sender_session_id"] != session_id(args.session_id):
            raise ValueError("The peer submission does not belong to this sender.")
        attempt = message.get("claude_peer", {})
        if attempt.get("status") not in ("SUBMITTING", args.status):
            raise ValueError("No matching Claude peer submission to record.")
        attempt["status"] = args.status
        return message
    if action == "resume":
        if not args.user_approved:
            raise ValueError("Use --user-approved only after the user explicitly approves resumption.")
        state["pause"] = None
        return {"pause": None}
    if action == "register":
        return register(state, args, cwd, args.session_id)
    if action == "capture":
        records = data
        identifiers = {session_id(value) for record in records if (value := event_session(args.provider, record))}
        if len(identifiers) != 1:
            raise ValueError("Expected exactly one native session ID in the provider output.")
        model = next((record["model"] for record in records if (
            args.provider == "claude" and record.get("type") == "system"
            and record.get("subtype") == "init" and isinstance(record.get("model"), str)
        )), None)
        session = register(state, args, cwd, identifiers.pop(), model)
        return observe(state, session, records, args.exit_code)

    if action == "observe" and args.session_id == "auto":
        routes = {
            (provider, session_id(value)) for provider in PROVIDERS for record in data
            if (value := event_session(provider, record))
        }
        if len(routes) != 1:
            raise ValueError("Expected exactly one native session ID in the callback event.")
        provider, native_id = routes.pop()
        session = registered(state, native_id)
        if session["provider"] != provider:
            raise ValueError("The callback provider does not match the registered session.")
    else:
        session = registered(state, args.session_id)
    if action == "rotate":
        return rotate(state, session, registered(state, args.replacement))
    if session["status"] == "RETIRED":
        raise ValueError("This session was retired. Refresh project routing.")
    if action == "observe":
        return observe(state, session, data, args.exit_code)
    if action == "pause":
        pause = set_pause(state, session, args.reason, args.reset_at)
        notify_parent(state, session, "A subscription limit was confirmed.")
        return pause
    if action == "update":
        if args.status == "RUNNING" and state["pause"]:
            raise ValueError("Development is paused. No new work can start.")
        if args.status == "RUNNING" and session["status"] == "RATE_LIMITED":
            raise ValueError("Verify the provider is available and mark the session IDLE first.")
        session.update(status=args.status, updated_at=now())
        if args.clear_task:
            session.update(current_task_id=None, request_id=None)
        if args.task or args.request:
            session.update(current_task_id=task_id(args.task) if args.task else None, request_id=args.request)
        return session

    messages = state["messages"]
    if action == "inbox":
        return [
            dict(message["envelope"], recipient_session_id=session["session_id"])
            for message in messages.values()
            if not message["delivered_at"]
            and message["recipient_session_id"] == session["session_id"]
            and not (state["pause"] and message["envelope"]["message_type"] == "TASK")
        ]
    if action == "receive" and session["provider"] == "claude":
        native_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
        if native_id and session_id(native_id) != session["session_id"]:
            raise ValueError("The message recipient does not match this Claude session.")
    message_id = session_id(args.message_id)
    message = messages.get(message_id)
    if not message or message["recipient_session_id"] != session["session_id"]:
        raise ValueError("This message is not addressed to this session.")
    if message["delivered_at"]:
        return None if action == "receive" else message
    if state["pause"] and message["envelope"]["message_type"] == "TASK":
        raise ValueError("Development is paused. No new TASK can be acknowledged.")
    message["delivered_at"] = now()
    if action == "receive":
        return dict(message["envelope"], recipient_session_id=session["session_id"])
    return message


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="working directory for the session record")
    commands = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "status"):
        commands.add_parser(name)
    for name in ("register", "capture"):
        command = commands.add_parser(name)
        command.add_argument("provider", choices=PROVIDERS)
        command.add_argument("role", choices=ROLES)
        command.add_argument("--model")
        command.add_argument("--parent")
        if name == "register":
            command.add_argument("session_id")
        else:
            command.add_argument("file", help="JSON or JSONL provider output, or - for UTF-8 stdin")
            command.add_argument("--exit-code", type=int)
    for name in ("update", "rotate", "observe", "pause", "inbox", "ack", "receive"):
        commands.add_parser(name).add_argument("session_id")
    commands.choices["rotate"].add_argument("replacement")
    commands.choices["update"].add_argument("--status", required=True, choices=STATUSES[:-2])
    commands.choices["update"].add_argument("--request")
    assignment = commands.choices["update"].add_mutually_exclusive_group()
    assignment.add_argument("--task")
    assignment.add_argument("--clear-task", action="store_true")
    commands.choices["pause"].add_argument("--reason", required=True)
    commands.choices["pause"].add_argument("--reset-at")
    commands.choices["observe"].add_argument("file", help="JSON or JSONL provider output, or - for UTF-8 stdin")
    commands.choices["observe"].add_argument("--exit-code", type=int)
    commands.choices["ack"].add_argument("message_id")
    commands.choices["receive"].add_argument("message_id")
    send = commands.add_parser("send")
    send.add_argument("file", help="JSON message envelope, or - for UTF-8 stdin")
    send.add_argument("--wake", action="store_true", help="reserve one native wake for the registered route")
    send.add_argument("--claude-relay", metavar="PEER_NAME", help="use one subscription turn through Claude CLI")
    peer = commands.add_parser("peer-result", help="record the Claude SendMessage outcome")
    peer.add_argument("session_id", help="registered sender UUID")
    peer.add_argument("message_id")
    peer.add_argument("--status", required=True, choices=PEER_RESULTS)
    commands.add_parser("resume").add_argument("--user-approved", action="store_true")
    args = parser.parse_args()
    if args.action == "update" and args.request and args.clear_task:
        parser.error("--request and --clear-task cannot be used together")
    if args.action == "send" and args.claude_relay is not None:
        if not args.wake or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.claude_relay):
            parser.error("--claude-relay requires --wake and a simple, unique local peer name.")

    try:
        data = None
        if args.action == "send":
            data = json.loads(input_text(args.file))
        if args.action in ("capture", "observe"):
            data = events(args.file, allow_empty=args.action == "observe" and bool(args.exit_code))
        roots, in_git = project_paths(Path(__file__).resolve().parents[1])
        cwd = args.cwd.resolve()
        if not cwd.is_dir() or not any(cwd.is_relative_to(root) for root in roots):
            raise ValueError("The working directory must belong to this project or a linked worktree.")
        runtime = runtime_directory(roots[0], in_git)
        state_path = runtime / "state.json"
        wake = None
        trigger = None
        with state_lock(runtime):
            protect_runtime(runtime, in_git)
            state = read_state(runtime)
            result = run(state, args, cwd, data)
            if args.action == "send" and args.wake:
                wake, trigger = prepare_wake(state, result, args.claude_relay)
            if args.action not in ("status", "inbox") or not state_path.exists():
                write_state(runtime, state)
        if wake:
            key, command_args = wake
            outcome = codex_wake(*command_args) if key == "codex_queue" else claude_relay_wake(*command_args)
            with state_lock(runtime):
                state = read_state(runtime)
                result = state["messages"][result["envelope"]["message_id"]]
                result[key] = outcome
                write_state(runtime, state)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"session: {error}\n")
    if trigger:
        result = dict(result, trigger=trigger)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
