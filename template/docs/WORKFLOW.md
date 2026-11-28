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
| [Supervisor](roles/supervisor.md) | One consultation brief and evidence needed to answer it | Assigned Director, Planner or Orchestrator |

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
2. For initial planning or major changes, start the Planner with a clean brief. Review the complete roadmap through production, recovery and owner acceptance. Each phase needs prerequisites, outputs, observable completion checks and a handoff. Detail the first executable phase and refine later phases from verified outcomes. Record plan approval separately from phase authorization and sensitive-operation approval in [PLAN.md](../PLAN.md).
3. Confirm the Orchestrator's provider, model, effort and Desktop preference explicitly before launch. Verify the created session's role, checkout, effective model and effort, requested Desktop project, and shared pause state. Supply the complete approved plan, constraints and parent route. Assign only one explicitly authorized phase or slice. Stop at its end or before any operation that needs separate approval.
4. The Director assigns a stable request ID, such as `REQ-001`, and sends a single request-level `TASK` to the Orchestrator with `task_id` set to `null`. The Orchestrator checks the approved scope and shared pause state. It allocates task IDs `TASK-001`, `TASK-002` and so on in the [Task Index](../tasks/INDEX.md), identifies dependencies, and assigns ownership. Use the [task template](../tasks/TEMPLATE.md) where a durable record is useful. A small subordinate action can inherit its parent's task ID when it reports within the same session.
5. The Orchestrator delegates directly by default. Add a Boss only when two or more concurrent streams need a combined result, more than one worktree patch needs coordination, or an independent review has several distinct questions. Choose the [worker model](MODELS.md#worker-fit) for the actual assignment. Workers can delegate independent, narrower subproblems within native limits. Start two or three independent workers at most by default. Every delegate needs the goal, expected output, ownership, scope, constraints, references, relevant installed [add-ons](PLUGINS.md), dependencies, acceptance checks and parent route. When a harness cannot spawn at the required depth, run the narrower work in the existing worker or let its parent spawn the child directly.
6. A worker confirms the scope, performs and verifies the assignment, and reports to its parent. Dependents start after inputs are available. Checkpoint before handing off. Verify against the relevant plan and user requirements before closing a task or integrating a change.
7. The Orchestrator records the terminal status, updates memory and sends one `REPORT` to the Director. Report review and verification separately. Include outstanding checks, blockers, references, available usage and a next step within scope. A failed connection or provisional result keeps its check open. After a phase, give the Planner a compact summary of capabilities, gaps, selected tools, verified results and pending decisions. Keep operational commands, transcripts and logs in execution records, with private evidence stored locally. The Director summarizes for the user.
8. If an independent idea arrives during execution, the Director records it in the [Idea Queue](../tasks/QUEUE.md) and tells the user it is queued. Honor any explicit request to steer or stop active work. After reporting, surface queued requests and await user approval before starting one.

Authorize local preparation, access checks, read-only inspection and changes to external systems separately when they carry different permissions or risks.

For parallel code edits use [worktrees and patch integration](WORKTREES.md). Research and read-only review can normally share an existing checkout. Pass the integration root to workers. Keep each worker's source changes in its assigned working directory and exchange small reports. The Director, Planner and Orchestrator update their shared records in the integration checkout.

### Optional direct execution for one task

Keep Director and Orchestrator separate by default. If the owner explicitly opts in and records the choice in this document, the Director may temporarily coordinate one authorized, noncritical task in the same session. It must need no plan revision, sensitive operation or worktree, and must not overlap an active assignment. The Director applies the Orchestrator's pause, delegation and closure rules, allocates the task ID in the shared index and reports directly to the owner. Use the normal registered route for other requests.

## Review and verification

The Planner marks critical work in the plan. The Orchestrator checks the classification again against the actual scope before dispatch. Treat security, authentication or secrets, sensitive data handling, migrations or deletions, destructive or irreversible changes, public contracts, payment or spending, and production deployment as critical. Validate acceptance criteria against observable evidence, such as test output, a build or an exact comparison. Record the writer model, acceptance evidence and these statuses in the [task record](../tasks/TEMPLATE.md):

- Review: `REVIEWED` for a completed independent review at the [required tier](MODELS.md#review-tier), `REVIEWED_SAME_TIER` for an independent review by an equal tier, `REVIEW_UNAVAILABLE` with its reason, or `NOT_REQUIRED` for trivial noncritical work covered by a deterministic check.
- Verification: `PASSED` when the required checks passed, `FAILED` when a check failed, or `NOT_RUN` with its reason when checks remain unrun. Record each check's actual result when evidence is mixed.

Close critical work only with `REVIEWED` and `PASSED`, or with `REVIEWED_SAME_TIER`, `PASSED` and an explicit owner waiver recorded in the task. If a stronger reviewer is unavailable, keep the task open and have the Director present the options: wait, authorize an available stronger reviewer, or explicitly accept a fresh same tier review. For noncritical work that needs review, the same tier is acceptable only under recorded owner approval. In either case, unresolved blocking findings or failed or unrun required checks keep the task open. A report can close the assigned execution slice while recording a blocked task. After material fixes or newly run checks, update their evidence before closure.

Record observable usage and rework in the task record when useful. At a phase boundary, summarize meaningful patterns in [memory](../MEMORY.md) and model choices that result from them in [decisions](DECISIONS.md). Compare first pass acceptance, rework and observed usage across comparable tasks before proposing a profile change. Use the existing task records and parent route for continuity.

## Ownership

| Path | Primary writer |
| --- | --- |
| `ASK_ME.md` | Starter maintainers |
| `AGENTS.md`, `CLAUDE.md`, `docs/WORKFLOW.md`, role instructions, provider configuration | Bootstrap or owner-approved revision |
| `PROJECT.md`, `tasks/QUEUE.md` | Director |
| `PLAN.md`, `docs/ARCHITECTURE.md` | Planner. Director records plan approval. Orchestrator updates the execution checklist. |
| `MEMORY.md`, `docs/DECISIONS.md`, `tasks/INDEX.md` | Orchestrator |
| `docs/MODELS.md`, `docs/PLUGINS.md` | Bootstrap or owner-approved revision. The owner may edit the PLUGINS.md Owner catalog directly. |
| `tasks/TASK-XXX.md` | Assigned worker. Orchestrator allocates the ID and assignment. |
| Local runtime and session registry | Controlled updates through the [communication guide](COMMUNICATION.md) |

Other agents propose edits to the writer. Separate the task document's lifecycle from the worker's session lifecycle. An interrupted session can be replaced while its task remains in progress or paused.

## Events and escalation

Use [the communication guide](COMMUNICATION.md) for cross-session delivery, pending reports, routing and safe session identity checks. Send a message for an assignment, meaningful blocker, terminal outcome, consultation or user decision. Use native completion events to recover failures and capture progress when available. A completed model turn is only a completed task when the task's outcome and evidence support it. Receive routine notifications without model-generated acknowledgments, periodic pings or automatic retries. The agent should save any undelivered terminal outcome for later delivery.

With [automatic routing](COMMUNICATION.md), Director records the authorized request against the approved plan, sends a `TASK` through the registered Orchestrator's route with that reference, and ends its turn. Orchestrator checks the reference, completes the approved work, updates the project records, and sends one `REPORT` through the registered Director's route. An eligible Director session wakes on the relay marker, receives the envelope, summarizes the result for the user, and ends its turn.

Escalate blockers through the immediate parent. The Planner or Orchestrator can propose a Supervisor consult. The Director can request one on the owner's behalf. Use one scoped question and one result. Record at least one trigger number in the brief:

1. A costly to reverse architecture decision, such as a persistent data model or system boundary.
2. A complex plan or decision affects multiple components, external systems or repositories and needs independent judgment about their boundaries or failure modes.
3. A decision materially affects security, privacy, sensitive data or spending.
4. Planner and Orchestrator still disagree after one exchange of written positions.
5. The owner asks for a second opinion.

Flag qualifying decisions during planning and resolve required consultations before execution authorization. Supervisor use is optional. When enabled, ask for approval per consult by default. Check the approved model and current access before launch. Fable requires authorization and paid credits require a separate decision. Record the question, evidence, options and approval reference. The Director asks the user for decisions that change agreed scope, technologies, risk or spending. Resolve small implementation choices within the approved plan.

## Checkpoint and rotation

Checkpoint at significant phase starts, task completion, important decisions, blockers, responsibility changes and any coordinated pause. Record progress where it belongs. Use the [checkpoint skill](../.agents/skills/project-checkpoint/SKILL.md) for the minimum content.

Keep memory aligned with the latest verified checkpoint and scope. Use the [Git publishing procedure](GIT_SETUP.md#publish-an-approved-checkpoint) for relevant changes. Continue within the approved scope when Git has nothing to commit.

Use native compaction for ordinary context pressure. Rotate when a clean session is materially better, such as after a major phase or when old context is interfering. Bring the previous session to a checkpoint, prepare a concise role and task handoff, start a clean candidate and verify it can continue. Use [the communication guide](COMMUNICATION.md) to move the route and retire the old assignment together. Let only one session own active work at a time. Preserve prior history and pending results.

## Coordinated pause

A confirmed limit on any active provider pauses new development project-wide. Distinguish exhausted subscription allowance from transient throttling, authentication failures and context overflows. Record known evidence and a reset time only if the provider states one.

1. Record `RATE_LIMITED` and set the shared project pause. Check project-wide pause before each dispatch or restart.
2. Bring workers to a safe boundary and checkpoint unfinished changes and reports. Avoid forceful interruption during operations that could damage project state. They may need a user or native session action to stop.
3. Record affected tasks as `PAUSED` in the index where appropriate. Notify the Director or save an undelivered report locally. Continue tracking resumable state without starting new development.
4. Resume only after user approval. Recheck provider availability and pending work. The Director may offer a substitution, such as Opus to Sol or Fable to explicitly requested Astra. Record any approved substitution in [model choices](MODELS.md). A substitution never starts automatically or clears the pause by itself.
