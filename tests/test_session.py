"""Exercise the local relay without a provider account or a model turn."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4


REPOSITORY = Path(__file__).resolve().parents[1]
SOURCE = REPOSITORY / "template" / "tools" / "session.py"


class SessionTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory(prefix="starter-session-")
        self.addCleanup(directory.cleanup)
        self.temp = Path(directory.name)
        self.project = self.temp / "project"
        self.install_helper(self.project)

    @staticmethod
    def install_helper(project):
        tools = project / "tools"
        tools.mkdir(parents=True)
        shutil.copyfile(SOURCE, tools / "session.py")

    def execute(self, *args, data=None, cwd=None, failure=None):
        process = subprocess.run(
            [sys.executable, str(self.project / "tools" / "session.py"), *args],
            cwd=cwd or self.project, input=data, capture_output=True, encoding="utf-8", check=False,
        )
        if failure:
            self.assertNotEqual(process.returncode, 0)
            self.assertIn(failure, process.stderr)
            return None
        self.assertEqual(process.returncode, 0, process.stderr)
        return json.loads(process.stdout)

    def register(self, provider, role, *args):
        identifier = str(uuid4())
        return self.execute("register", provider, role, identifier, *args)["session_id"]

    def test_delivery_and_rotation(self):
        director = self.register("codex", "director")
        worker = self.register("claude", "development-worker", "--parent", director)
        envelope = {
            "message_id": str(uuid4()), "request_id": "REQ-001", "task_id": "TASK-001",
            "message_type": "REPORT", "sender_role": "development-worker", "sender_session_id": worker,
            "recipient_role": "director", "recipient_session_id": director, "payload": "Verification passed.",
        }
        queued = self.execute("send", "-", data=json.dumps(envelope))
        self.assertIsNone(queued["delivered_at"])
        retry = self.execute("send", "-", data=json.dumps(dict(envelope, message_id=str(uuid4()))))
        self.assertEqual(queued, retry)
        self.execute("ack", worker, envelope["message_id"], failure="not addressed")

        replacement = self.register("codex", "director")
        self.execute("update", replacement, "--status", "IDLE")
        self.execute("rotate", director, replacement)
        self.execute("inbox", director, failure="retired")
        self.assertEqual(self.execute("inbox", replacement), [dict(envelope, recipient_session_id=replacement)])
        retry = self.execute("send", "-", data=json.dumps(envelope))
        self.assertEqual(retry["recipient_session_id"], replacement)
        status = self.execute("status")
        self.assertEqual(status["sessions"][worker]["parent_session_id"], replacement)
        self.assertIsNotNone(self.execute("ack", replacement, envelope["message_id"])["delivered_at"])
        self.assertEqual(self.execute("inbox", replacement), [])
        new_worker = self.register("claude", "development-worker")
        self.execute("update", new_worker, "--status", "IDLE")
        rotated_worker = self.execute("rotate", worker, new_worker)
        self.assertEqual(rotated_worker["parent_session_id"], replacement)

    def test_capture_callbacks_and_shared_pause(self):
        director = self.register("claude", "director")
        worker = str(uuid4())
        capture = "\n".join(json.dumps(record) for record in (
            {"type": "thread.started", "thread_id": worker}, {"type": "turn.completed"},
        ))
        result = self.execute("capture", "codex", "development-worker", "-", "--parent", director, data=capture)
        self.assertEqual(result["session_id"], worker)
        self.assertEqual(result["status"], "STARTING")
        self.execute("update", worker, "--status", "RUNNING", "--task", "TASK-001", "--request", "REQ-001")
        self.execute("observe", worker, "-", data=json.dumps({"type": "turn.failed"}))
        self.assertEqual(self.execute("status")["sessions"][worker]["status"], "FAILED")
        self.assertIsNone(self.execute("status")["pause"])
        failure = json.dumps({
            "method": "turn/completed", "params": {"threadId": worker, "turn": {
                "status": "failed", "error": {"codexErrorInfo": "usageLimitExceeded"},
            }},
        })
        self.execute("observe", worker, "-", data=failure)
        self.execute("observe", worker, "-", data=failure)
        self.assertEqual(self.execute("status")["pause"]["session_id"], worker)
        self.assertEqual(len(self.execute("inbox", director)), 2)
        task = {
            "message_id": str(uuid4()), "request_id": "REQ-002", "task_id": "TASK-002",
            "message_type": "TASK", "sender_role": "director", "sender_session_id": director,
            "recipient_role": "development-worker", "recipient_session_id": worker, "payload": "Run checks.",
        }
        self.execute("send", "-", data=json.dumps(task), failure="paused")
        self.execute("update", worker, "--status", "RUNNING", failure="paused")
        self.execute("resume", failure="explicitly approves")
        self.execute("resume", "--user-approved")
        self.execute("update", worker, "--status", "RUNNING", failure="mark the session IDLE")
        self.execute("update", worker, "--status", "IDLE")
        self.assertIsNone(self.execute("status")["pause"])

    def test_claude_failure_does_not_infer_quota(self):
        identifier = str(uuid4())
        init = {"type": "system", "subtype": "init", "session_id": identifier, "model": "test-model"}
        captured = self.execute("capture", "claude", "planner", "-", data=json.dumps(init, indent=2))
        self.assertEqual(captured["model"], "test-model")
        hook = {"hook_event_name": "StopFailure", "session_id": identifier, "error": "rate_limit"}
        self.execute("observe", "auto", "-", data=json.dumps(hook))
        self.assertIsNone(self.execute("status")["pause"])
        self.execute("pause", identifier, "--reason", "Confirmed subscription limit")
        self.assertEqual(self.execute("status")["sessions"][identifier]["status"], "RATE_LIMITED")

    def test_request_level_assignment_correlates_failure(self):
        director = self.register("codex", "director")
        orchestrator = self.register("claude", "orchestrator", "--parent", director)
        assignment = {
            "message_id": str(uuid4()), "request_id": "REQ-001", "task_id": None,
            "message_type": "TASK", "sender_role": "director", "sender_session_id": director,
            "recipient_role": "orchestrator", "recipient_session_id": orchestrator,
            "payload": "Coordinate the approved plan.",
        }
        self.execute("send", "-", data=json.dumps(assignment))
        self.assertEqual(self.execute("inbox", orchestrator), [assignment])
        self.execute("ack", orchestrator, assignment["message_id"])
        self.execute("update", orchestrator, "--status", "RUNNING", "--request", "REQ-001")
        failed = self.execute("observe", orchestrator, "-", "--exit-code", "9", data="")
        self.assertEqual(failed["status"], "FAILED")
        blocker = self.execute("inbox", director)[0]
        self.assertEqual(blocker["message_type"], "BLOCKER")
        self.assertEqual(blocker["request_id"], "REQ-001")
        self.assertIsNone(blocker["task_id"])

    @unittest.skipUnless(shutil.which("git"), "Git is required for the linked-worktree check")
    def test_git_ignores_state_and_shares_concurrent_updates(self):
        subprocess.run(["git", "init", "--quiet"], cwd=self.project, check=True)
        with ThreadPoolExecutor(max_workers=4) as workers:
            ids = list(workers.map(lambda _: self.register("codex", "subagent"), range(8)))
        self.assertEqual(set(self.execute("status")["sessions"]), set(ids))
        subprocess.run(["git", "check-ignore", ".runtime/state.json"], cwd=self.project, check=True, capture_output=True)
        subprocess.run(["git", "add", "-f", ".runtime/state.json"], cwd=self.project, check=True)
        self.execute("status", failure="tracked files")

        self.project = self.temp / "cloned"
        worktree = self.temp / "linked"
        subprocess.run(["git", "clone", "--quiet", str(REPOSITORY), str(self.project)], check=True)
        subprocess.run(["git", "worktree", "add", "--quiet", "--detach", str(worktree), "HEAD"], cwd=self.project, check=True)
        self.install_helper(self.project)
        self.install_helper(worktree)
        identifier = self.register("codex", "director")
        self.assertIn(identifier, self.execute("status", cwd=worktree)["sessions"])
        result = subprocess.run(
            [sys.executable, str(worktree / "tools" / "session.py"), "status"],
            cwd=worktree, capture_output=True, encoding="utf-8", check=True,
        )
        self.assertIn(identifier, json.loads(result.stdout)["sessions"])
        self.assertFalse((worktree / ".runtime").exists())


if __name__ == "__main__":
    unittest.main()
