# Project workflow

## Roles and routes

| Role | Default context beyond AGENTS.md | Reports to |
| --- | --- | --- |
| [Bootstrap](../ASK_ME.md) | Existing project settings, installed files, model and add-on choices, runtime setup | User |
| [Director](roles/director.md) | Project brief, memory, plan approval, task index, idea queue and relevant routes | User |
| [Planner](roles/planner.md) | Clarified requirements, existing plan and architecture, selected research | Director |
| [Orchestrator](roles/orchestrator.md) | Approved plan, relevant requirements, architecture and decisions, memory, task index and runtime | Director |
| [Research Boss](roles/research-boss.md) | Research brief, constraints and relevant sources | Orchestrator |
| [Develop Boss](roles/develop-boss.md) | Approved work scope, task dependencies, write limits and worktree instructions | Orchestrator |
| [Review Boss](roles/review-boss.md) | Relevant diff, acceptance criteria and verification references | Orchestrator |
| [Task workers](roles/worker.md) | Assigned task, narrowly scoped files and parent route | Assigned Boss, Planner or Orchestrator |
| [Supervisor](roles/supervisor.md) | One consultation brief and evidence needed to answer it | Planner or Orchestrator |

Bootstrap prepares the environment once. The Director and Orchestrator persist as roles across session rotations. Activate the Planner for initial design and major approved revisions. Activate Bosses for work that benefits from coordination. Use the Supervisor on demand. The same role can use different physical sessions over time. A business task, native subagent, Git branch and Git worktree have their own lifecycles.

### Load context in layers

1. Read the global rules.
2. Open the project records you need.
3. Read the assigned role and relevant parts of this workflow.
4. Load the assigned task and the listed files or references.
5. Read specific runtime information when routing, checking pause or recovering a session.

Read targeted sources and diffs. Keep transcripts and wholesale repository scans out of routine handoffs. Use native permissions or a read-only sandbox when actual access needs to be restricted.

## Approval and execution

1. After [Bootstrap](../ASK_ME.md), the user brings a request to the Director. The Director clarifies outcomes and constraints and updates [PROJECT.md](../PROJECT.md).
2. For initial planning or major changes, start the Planner with a clean brief. The Planner proposes a plan and architecture. The Director presents the plan revision to the user and records the approval in [PLAN.md](../PLAN.md) only when received.
3. Start the Orchestrator in a clean session after plan approval. Supply the approved revision, relevant constraints and file references, role hierarchy, model choices and actual parent route when available. Wait for user authorization to start the specific request or phase.
4. The Director assigns a stable request ID, such as `REQ-001`, and sends a single request-level `TASK` to the Orchestrator with `task_id` set to `null`. The Orchestrator checks the approved scope and shared pause state. It allocates task IDs `TASK-001`, `TASK-002` and so on in the [Task Index](../tasks/INDEX.md), identifies dependencies, and assigns ownership. Use the [task template](../tasks/TEMPLATE.md) where a durable record is useful. A small subordinate action can inherit its parent's task ID when it reports within the same session.
5. The Orchestrator delegates directly for small work. Add a Boss for coordinated streams or independent review when the scope, risk or complexity warrants it. Workers can delegate independent, narrower subproblems within native limits. Start two or three independent workers at most by default. Every delegate needs the goal, expected output, ownership, scope, constraints, references, dependencies, acceptance checks and parent route. When a harness cannot spawn at the required depth, run the narrower work in the existing worker or let its parent spawn the child directly.
6. A worker confirms the scope, performs and verifies the assignment, and reports to its parent. Dependents start after inputs are available. Checkpoint before handing off. Verify against the relevant plan and user requirements before closing a task or integrating a change.
7. The Orchestrator records the terminal status, updates memory and sends one `REPORT` to the Director. Include finished work, outstanding work, verification, blockers requiring a decision, references and a next step within scope. The Director summarizes for the user.
8. If an independent idea arrives during execution, the Director records it in the [Idea Queue](../tasks/QUEUE.md) and tells the user it is queued. Honor any explicit request to steer or stop active work. After reporting, surface queued requests and await user approval before starting one.

For parallel code edits use [worktrees and patch integration](WORKTREES.md). Research and read-only review can normally share an existing checkout. Pass the integration root to workers. Keep each worker's source changes in its assigned working directory and exchange small reports. The Director, Planner and Orchestrator update their shared records in the integration checkout.

## Ownership

| Path | Primary writer |
| --- | --- |
| `ASK_ME.md` | Starter maintainers |
| `AGENTS.md`, `CLAUDE.md`, `docs/WORKFLOW.md`, role instructions, provider configuration | Bootstrap or owner-approved revision |
| `PROJECT.md`, `tasks/QUEUE.md` | Director |
| `PLAN.md`, `docs/ARCHITECTURE.md` | Planner. Director records plan approval. Orchestrator updates the execution checklist. |
| `MEMORY.md`, `docs/DECISIONS.md`, `tasks/INDEX.md` | Orchestrator |
| `docs/MODELS.md`, `docs/PLUGINS.md` | Bootstrap or owner-approved revision |
| `tasks/TASK-XXX.md` | Assigned worker. Orchestrator allocates the ID and assignment. |
| Local runtime and session registry | Controlled updates through the [communication guide](COMMUNICATION.md) |

Other agents propose edits to the writer. Separate the task document's lifecycle from the worker's session lifecycle. An interrupted session can be replaced while its task remains in progress or paused.

## Events and escalation

Use [the communication guide](COMMUNICATION.md) for cross-session delivery, pending reports, routing and safe session identity checks. Send a message for an assignment, meaningful blocker, terminal outcome, consultation or user decision. Use native completion events to recover failures and capture progress when available. A completed model turn is only a completed task when the task's outcome and evidence support it. Receive routine notifications without model-generated acknowledgments, periodic pings or automatic retries. The agent should save any undelivered terminal outcome for later delivery.

With [automatic Codex routing](COMMUNICATION.md#automatic-codex-delivery), Director records the authorized request against the approved plan, sends a `TASK` with that reference, and ends its turn. Orchestrator checks the reference, completes the approved work, updates the project records, and sends one `REPORT`. The queued report wakes an eligible Director session, which summarizes the result for the user and ends its turn.

Escalate blockers through the immediate parent. The Planner and Orchestrator can consult the Supervisor for a difficult technical decision. The Director asks the user for any decision that changes agreed project scope, technologies, risk or spending. Resolve small implementation choices within the approved plan.

## Checkpoint and rotation

Checkpoint at significant phase starts, task completion, important decisions, blockers, responsibility changes and any coordinated pause. Record progress where it belongs. Use the [checkpoint skill](../.agents/skills/project-checkpoint/SKILL.md) for the minimum content.

Use native compaction for ordinary context pressure. Rotate when a clean session is materially better, such as after a major phase or when old context is interfering. Bring the previous session to a checkpoint, prepare a concise role and task handoff, start a clean candidate and verify it can continue. Use [the communication guide](COMMUNICATION.md) to move the route and retire the old assignment together. Let only one session own active work at a time. Preserve prior history and pending results.

## Coordinated pause

A confirmed limit on any active provider pauses new development project-wide. Distinguish exhausted subscription allowance from transient throttling, authentication failures and context overflows. Record known evidence and a reset time only if the provider states one.

1. Record `RATE_LIMITED` and set the shared project pause. Check project-wide pause before each dispatch or restart.
2. Bring workers to a safe boundary and checkpoint unfinished changes and reports. Avoid forceful interruption during operations that could damage project state. They may need a user or native session action to stop.
3. Record affected tasks as `PAUSED` in the index where appropriate. Notify the Director or save an undelivered report locally. Continue tracking resumable state without starting new development.
4. Resume only after user approval. Recheck provider availability and pending work. Keep the approved provider or ask for an explicit change if necessary.
