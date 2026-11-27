# Models and effort

Choose models you can select in the signed-in native client. Marketing names, model IDs, effort options, and access can vary by account and client version. Record the chosen provider, model and effort by role in [the project's `docs/MODELS.md`](../template/docs/MODELS.md). Edit that file when a model changes. The native subagent definitions use provider defaults or inheritance unless project owners add overrides.

## Starting profiles

Use the [role-by-role starting profiles](../template/docs/MODELS.md#starting-profiles) that Bootstrap reads in the installed project. Check availability in the client before saving the active profile.

Use the [worker fit and review tiers](../template/docs/MODELS.md#worker-fit) to assign work. Fable is reserved for authorized consultations or reviews. Astra is selected only at the owner's explicit request. If a model needs paid credits, obtain separate approval. A confirmed subscription limit uses the coordinated project pause. [Claude Code model availability and usage credits](https://code.claude.com/docs/en/model-config)

Benchmark results depend on the evaluation and effort. API prices describe token billing. Confirm subscription access and limits separately in the signed-in client. Where an installed client exposes structured usage, record the source. Label an API-equivalent estimate as an estimate and record an actual charge only when independently confirmed. Use `unavailable` for counts or costs the client does not expose.

## Select the model in the client

- Codex model selectors include `gpt-6.2-sol`, `gpt-6-luna` and, only on explicit owner request, `gpt-6.2-astra`. Use `/model` to choose an available model and reasoning level, or CLI arguments such as `codex --model gpt-6.2-sol -c 'model_reasoning_effort="medium"'`. Check the value in the client before dispatching work. [Codex models](https://learn.chatgpt.com/docs/models) · [Codex CLI reference](https://learn.chatgpt.com/docs/cli/reference)
- Claude Code documents aliases including `opus`, `sonnet`, `haiku`, and `fable`. Use `/model` and `/effort` or launch a session with, for example, `claude --model opus --effort high`. The display shows which model and effort the current account can use. [Claude Code model configuration](https://code.claude.com/docs/en/model-config)

If the chosen model is unavailable or your subscription is limited, checkpoint the task and ask Director for a user decision. The project configuration should reflect any approved change. [Limit handling](../template/docs/WORKFLOW.md)
