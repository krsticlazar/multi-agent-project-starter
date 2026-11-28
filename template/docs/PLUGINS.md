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
- When writing a brief, the parent names the installed add-ons that fit the task and the catalog guidance that applies. A delegate uses only add-ons available in its own session. If a named add-on is unavailable there, it continues with native tools and says so in its report.

## Owner catalog

This section holds the owner's own notes on plugins, MCP servers and skills, in any format. The owner can paste a personal catalog here before Bootstrap, or give it to Bootstrap in chat. Bootstrap keeps the text as written and records each entry's status in the table above. The owner may edit this section directly at any time.

The table is authoritative for what is available in this project. The catalog is guidance on when and how to use an add-on. Use only entries whose table status is `Installed`. An entry listed here but not installed stays `Pending` or `Unavailable` until the owner approves setup.

Leave credentials, tokens and private endpoint details out of this section.

_No owner catalog yet._
