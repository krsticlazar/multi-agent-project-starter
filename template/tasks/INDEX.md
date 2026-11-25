# Task index

The Orchestrator maintains this table in the integration checkout. Workers update the assigned [task document](TEMPLATE.md) and report their outcome to their parent.

| Task ID | Request ID | Title | Owner | Dependencies | Status | Outcome or reference |
| --- | --- | --- | --- | --- | --- | --- |

Use `PENDING`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`, `FAILED`, `CANCELLED` or `PAUSED`. Keep task status independent of session status.
