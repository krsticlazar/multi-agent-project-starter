# Model choices

Bootstrap records the actual operating profile here. Native adapters inherit the selected model unless the launcher or supported spawn tool supplies a model. Select the provider for each new independent session from the agreed profile. Change choices only with user approval.

## Active configuration

- Profile:
- Approved providers and subscription types:
- Client or workspace constraints:
- Desktop visibility by role and project:
- Planning mode: Planner led
- Supervisor consult approval: per consult when enabled (off by default)
- Allow same tier review for noncritical tasks: no unless the owner opts in

Confirm each role independently before session creation. A model approved for development or research leaves the Orchestrator's model and effort open. Obtain separate approval when a model uses paid credits.

| Role | Provider | Confirmed model selector or provider default | Effort or provider default |
| --- | --- | --- | --- |
| Bootstrap | | | |
| Director | | | |
| Planner | | | |
| Orchestrator | | | |
| Supervisor | | | |
| Research Boss | | | |
| Research Worker | | | |
| Develop Boss | | | |
| Development Worker | | | |
| Review Boss | | | |
| Review Worker | | | |
| Bounded Mechanical Worker | | | |

## Starting profiles

| Role | Codex + Claude Code | Codex only | Claude Code only |
| --- | --- | --- | --- |
| Bootstrap, Director | Sol medium | Sol medium | Sonnet medium |
| Planner | Opus medium | Sol high | Opus medium |
| Orchestrator | Sol medium | Sol medium | Sonnet medium, or Opus medium for complex phases |
| Supervisor | Off by default. Authorized Fable when available, or a scoped Opus consult | Off by default. Astra only on explicit owner request | Off by default. Authorized Fable when available, or a scoped Opus consult |
| Substantive Research Worker | Sonnet medium under Opus, Sol medium under Sol | Sol medium | Sonnet medium |
| Development Worker | Sol medium in the Codex chain, Sonnet medium in the Claude chain | Sol medium | Sonnet medium |
| Bounded Mechanical Worker | Luna low to medium under Sol, Haiku or equivalent in Claude | Luna low to medium | Haiku or available equivalent |
| Bosses when needed | Research and Develop: suitable substantive worker model. Review: use the writer-to-reviewer table | Same rule with Codex models | Same rule with Claude models |

Opus leads planning in the mixed profile. If the owner chooses to conserve Opus quota, Sol may draft the roadmap, phases and checks, and Opus reviews and refines architecture, risks and critical tasks before the plan goes to the Director. Record the selected mode above. Select Astra only on explicit owner request. Check Fable access on the signed-in client and obtain separate approval for any paid credits.

## Worker fit

- Use Luna or an equivalent mechanical worker for file discovery, extraction from known fields, formatting, mechanical edits or routine boilerplate. The brief must give a deterministic pass/fail check the parent can verify independently, such as an exact diff, schema check or lint result.
- Use Sol or Sonnet for research that needs source evaluation, diagnosis with an unknown cause, behavioral changes, or work whose acceptance requires judgment. Prefer delegation within the parent's provider. Choose across providers based on tool fit and approved availability.

## Review tier

Independent code review uses a reviewer at least one tier above the writer in the project profile. Apply the mapping to each assigned change. A reviewer covering a combined diff must qualify for all writers it covers. Follow the [closure rules](WORKFLOW.md#review-and-verification) if the intended reviewer is unavailable.

| Writer | Eligible reviewer in the starting profiles |
| --- | --- |
| Luna | Sonnet or Sol |
| Haiku or equivalent | Sonnet in Claude, or an approved higher tier |
| Sonnet | Sol or Opus |
| Sol | Opus, or Fable or Astra with the applicable owner authorization. In Codex only, a tier above may be unavailable |
| Opus | Fable with the applicable owner authorization. Otherwise the tier above may be unavailable |

These are role tiers for this workflow. Benchmark scores and API prices cannot establish subscription access, quotas, or review quality at the chosen effort. Actual availability and effort support depend on the signed-in client. Stay within the user's selected provider set.

- Codex documents `gpt-6.2-sol`, `gpt-6.2-astra` and `gpt-6-luna`. Choose through the model picker or use `codex --model MODEL -c model_reasoning_effort=EFFORT` with values the installed client lists for that model. For compatible subagent tools, pass the approved model and effort at spawn. [Model reference](https://learn.chatgpt.com/docs/models) · [CLI reference](https://learn.chatgpt.com/docs/cli/reference)
- Claude Code accepts aliases such as `sonnet`, `opus`, `haiku` and `fable` where available. Choose with the provider UI or `claude --model MODEL --effort EFFORT` when those settings are supported. Native subagents may inherit the parent's model. Verify the chosen model and effort before recording an override. [Model configuration](https://code.claude.com/docs/en/model-config) · [Subagent selection](https://code.claude.com/docs/en/sub-agents#choose-a-model)
