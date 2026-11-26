# Models and effort

Choose models you can select in the signed-in native client. Marketing names, model IDs, effort options, and access can vary by account and client version. Record the chosen provider, model and effort by role in [the project's `docs/MODELS.md`](../template/docs/MODELS.md). Edit that file when a model changes. The native subagent definitions use provider defaults or inheritance unless project owners add overrides.

## Starting profiles

Use the [role-by-role starting profiles](../template/docs/MODELS.md#starting-profiles) that Bootstrap reads in the installed project. Check availability in the client before saving the active profile.

Use the simplest model and delegation path that can verify the result. A Claude Code Fable seat may show a usage credit requirement. Select an included model unless the project owner explicitly approves separate billing. The starter never reroutes a job to a different provider when a limit is hit. [Claude Code model availability and usage credits](https://code.claude.com/docs/en/model-config)

## Select the model in the client

- Codex documents `gpt-6.2-sol` and `gpt-6-luna` for accounts with access. Use `/model` to choose an available model and reasoning level, or CLI arguments such as `codex --model gpt-6.2-sol -c 'model_reasoning_effort="medium"'`. Check the value in the client before dispatching work. [Codex models](https://learn.chatgpt.com/docs/models) · [Codex CLI reference](https://learn.chatgpt.com/docs/cli/reference)
- Claude Code documents aliases including `opus`, `sonnet`, `haiku`, and `fable`. Use `/model` and `/effort` or launch a session with, for example, `claude --model opus --effort high`. The display shows which model and effort the current account can use. [Claude Code model configuration](https://code.claude.com/docs/en/model-config)

If the chosen model is unavailable or your subscription is limited, checkpoint the task and ask Director for a user decision. The project configuration should reflect any approved change. [Limit handling](../template/docs/WORKFLOW.md)
