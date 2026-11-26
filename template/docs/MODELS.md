# Model choices

Bootstrap records the actual operating profile here. Native adapters inherit the selected model unless the launcher or supported spawn tool supplies a model. Select the provider for each new independent session from the agreed profile. Change choices only with user approval.

## Active configuration

- Profile:
- Approved providers and subscription types:
- Client or workspace constraints:
- Desktop visibility by role and project:

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
| Routine Subagent | | | |

## Starting profiles

| Role | Codex + Claude Code | Codex only | Claude Code only |
| --- | --- | --- | --- |
| Bootstrap, Director | Sol medium | Sol medium | Sonnet medium |
| Planner | Opus high | Astra high | Opus high |
| Orchestrator | Sol medium or Opus high | Sol medium or high | Sonnet medium or Opus high |
| Supervisor | Fable high when available | Astra high | Fable or Opus high |
| Research Boss | Sonnet medium | Sol medium | Sonnet medium |
| Research Worker | Sonnet medium or Luna low to medium | Luna low to medium | Sonnet low to medium |
| Develop Boss, Development Worker | Sol medium | Sol medium | Sonnet medium |
| Review Boss | Sol medium | Sol medium | Sonnet medium |
| Review Worker | Luna or Sol medium | Luna or Sol medium | Sonnet medium |
| Routine Subagent | Luna or equivalent | Luna low to medium | Haiku or available equivalent |

Use the best available model for a hard design question and a faster available model for bounded work. Actual availability and effort support depend on the client, account and model. Stay within the user's selected provider set.

- Codex documents `gpt-6.2-sol`, `gpt-6.2-astra` and `gpt-6-luna`. Choose through the model picker or use `codex --model MODEL -c model_reasoning_effort=EFFORT` with values the installed client lists for that model. For compatible subagent tools, pass the approved model and effort at spawn. [Model reference](https://learn.chatgpt.com/docs/models) · [CLI reference](https://learn.chatgpt.com/docs/cli/reference)
- Claude Code accepts aliases such as `sonnet`, `opus`, `haiku` and `fable` where available. Choose with the provider UI or `claude --model MODEL --effort EFFORT` when those settings are supported. Native subagents may inherit the parent's model. Verify the chosen model and effort before recording an override. [Model configuration](https://code.claude.com/docs/en/model-config) · [Subagent selection](https://code.claude.com/docs/en/sub-agents#choose-a-model)
