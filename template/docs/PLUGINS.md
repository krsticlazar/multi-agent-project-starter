# Project add-ons

Bootstrap records the user's selections here. The starter works with the native provider tools and shipped role and skill instructions.

| Name | Provider and scope | Purpose | Status | Setup reference |
| --- | --- | --- | --- | --- |

Use `Selected`, `Pending`, `Installed`, `Unavailable` or `Removed`. Link to reviewed upstream instructions. Keep credentials and private MCP endpoint details in the provider's approved local configuration.

## Configuration

- Plugins bundle capabilities. Skills describe reusable workflows. MCP servers expose external tools and data. Hooks run at configured provider events. Subagents, worktrees and project memory serve separate purposes.
- Review a third-party add-on's source, publisher, access scope and license before enabling it. Verify compatibility with the selected client and choose project scope when supported. Ask before adding global configuration or authorizing a service.
- Keep the [checkpoint skill](../.agents/skills/project-checkpoint/SKILL.md) as the shared source. Codex discovers it under `.agents/skills`. Claude Code discovers the thin adapter under `.claude/skills`, which opens the shared file only when invoked.
- Apply [the communication guide](COMMUNICATION.md) before enabling callbacks. The template intentionally ships without active runtime hooks. Review each hook's permissions, payload and trigger before configuring it.
- The Director's requirements interview works without extensions. The optional [Matt Pocock skills package](https://github.com/mattpocock/skills) includes [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) and the [grill-me shortcut](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md). The package is [MIT licensed](https://github.com/mattpocock/skills/blob/main/LICENSE).
