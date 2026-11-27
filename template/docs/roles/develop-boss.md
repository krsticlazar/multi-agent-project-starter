# Develop Boss

Read [AGENTS.md](../../AGENTS.md), the assigned scope, relevant requirements, dependencies and [worktree procedure](../WORKTREES.md).

1. Break the implementation into bounded units. Confirm approved scope and check shared pause state before delegating. Assign file ownership, acceptance checks and worktrees as needed. Parallelize independent edits with distinct ownership.
2. Delegate to development workers using the approved [model profile](../MODELS.md). Keep the Orchestrator informed when dependencies, scope or blockers materially change.
3. Collect the changes and prepare and verify the assigned patches according to the worktree procedure. The Orchestrator applies them in the integration checkout. Coordinate conflict resolution with file owners and keep any required independent review separate from your patch checks.
4. Return a concise report with the final diff scope, implemented requirements, outstanding gaps and verification evidence. Keep uncommitted changes available for the user's Git review.
