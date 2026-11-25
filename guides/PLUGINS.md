# Plugins, skills, and MCP

Start with the shipped agent definitions and checkpoint skill. Record optional additions in the project's [`docs/PLUGINS.md`](../template/docs/PLUGINS.md) during Bootstrap. Check the installation scope, granted tools, data sharing, and terms before opting in. Keep credentials in the provider's supported credential store and out of project files.

## Optional catalog

The install paths and licenses below come from the publishers. The starter does not install or verify these components on your account.

| Addition | When to use it | Compatibility and installation |
| --- | --- | --- |
| Matt Pocock's `grill-me` | An optional interview skill for fleshing out ideas. It calls `grilling`, which surfaces and resolves design choices in rounds. | MIT. The publisher documents the `mattpocock-skills` plugin for Claude Code and Codex. [Install and skill index](https://github.com/mattpocock/skills) · [Grilling instructions](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) |
| Codex plugin for Claude Code | Delegate a scoped Codex task or review code from Claude Code. | Apache-2.0. In Claude Code, add marketplace `openai/codex-plugin-cc`, install `codex@openai-codex`, reload plugins, then run `/codex:setup`. A signed-in Codex CLI is needed. [OpenAI plugin](https://github.com/openai/codex-plugin-cc) |
| Context7 | Look up current library documentation with an MCP tool. | MIT repository. Context7 documents plugins and OAuth for both clients. Choose the manual method if you need to control exactly which configuration files change. [Context7 installation](https://context7.com/docs/installation) · [License](https://github.com/upstash/context7) |
| Superpowers | Add a specific development workflow where it fits the approved project process. | MIT. Follow the provider-specific steps for the Claude Code, Codex app, or Codex CLI integration. Check for overlapping planning and delegation policies. [Superpowers installation](https://github.com/obra/superpowers#installation) |
| Code Simplifier | Simplify the implementation of a scoped change while preserving behavior. | Apache-2.0 Claude Code option. Install `code-simplifier@claude-plugins-official` through the native plugin system. A scoped simplification prompt works on either client. [Anthropic marketplace listing](https://claude.com/plugins/code-simplifier) · [License](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/LICENSE) |
| Playwright MCP | Browser interaction for a project that needs web UI verification. | Apache-2.0. The repository documents Node.js prerequisites and native Claude Code and Codex MCP installation. Limit browser access to the intended test workspace. [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp) |
| GitHub MCP | Read GitHub data that local Git and `gh` cannot provide. | MIT. Use the official client guide and grant only needed access. Choose read-only tools when the task is analysis. [GitHub MCP Server](https://github.com/github/github-mcp-server) |

## Scope and capabilities

- A **plugin** packages capabilities that may include skills, agents, hooks, or MCP servers. Inspect provider-specific installation scope before running a marketplace command. [Codex plugins](https://learn.chatgpt.com/docs/plugins) · [Claude Code plugins](https://code.claude.com/docs/en/discover-plugins)
- A **skill** loads reusable instructions for a task. The starter keeps a shared checkpoint skill in `.agents/skills/` with a light Claude Code adapter where appropriate. [Codex skills](https://learn.chatgpt.com/docs/build-skills) · [Claude Code skills](https://code.claude.com/docs/en/skills)
- **MCP** exposes tools. For Codex, review a project-scoped `.codex/config.toml`; the CLI `codex mcp add` typically writes user settings. For Claude Code, `claude mcp add --scope project` creates or updates `.mcp.json`. Project settings are subject to trust and approval. [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp) · [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- A **hook** runs at a native lifecycle event. Review what it executes and keep it project-scoped. A stopped turn is insufficient evidence of task completion. [Codex hooks](https://learn.chatgpt.com/docs/hooks) · [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- A **subagent** receives a scoped assignment. A **worktree** isolates filesystem changes. **Project memory** preserves durable facts in the project files. Those components remain useful without external add-ons. [Project workflow](../template/docs/WORKFLOW.md)
