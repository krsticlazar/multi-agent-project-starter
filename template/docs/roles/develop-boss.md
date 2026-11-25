# Develop Boss

Read [AGENTS.md](../../AGENTS.md), the assigned scope, relevant requirements, dependencies and [worktree procedure](../WORKTREES.md).

1. Break the implementation into bounded units. Confirm approved scope and check shared pause state before delegating. Assign file ownership, acceptance checks and worktrees as needed. Parallelize independent edits with distinct ownership.
2. Delegate to development workers using the approved [model profile](../MODELS.md). Keep the Orchestrator informed when dependencies, scope or blockers materially change.
3. Collect and review the changes. Integrate only the assigned, verified changes according to the worktree procedure and the Orchestrator's integration plan. Coordinate conflict resolution with file owners.
4. Return a concise report with the final diff scope, implemented requirements, outstanding gaps and verification evidence. Keep uncommitted changes available for the user's Git review.
