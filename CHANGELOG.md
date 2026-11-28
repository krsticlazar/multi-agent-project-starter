# Changelog

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

## [Unreleased]

### Added

- Reusable project template with a Bootstrap interview, shared project knowledge, task management, and scoped agent instructions for Codex and Claude Code.
- Local session and communication workflow with durable handoffs and a coordinated usage pause.
- PowerShell and Bash installers that preserve existing project files, including hidden provider configuration.
- Installation, model, plugin, troubleshooting, and contribution guides, plus checks for archive and installer behavior.
- Native Codex wake for registered local sessions, with one submission per relay envelope and a one-time recipient receipt.
- Claude peer handoffs and an opt-in CLI wake for a verified live Claude recipient. Claude sessions can also use the native Codex queue.
- GitHub-first bootstrap choices, local-only workflow records, phase-scoped execution approvals, and quoted Claude relay names with spaces.
- A one-line PowerShell installation through `scripts/web-install.ps1` that downloads the GitHub archive, checks its ref, and runs the existing installer, with optional commit pinning.
- An Owner catalog section in `docs/PLUGINS.md` for the owner's own plugin, MCP and skill notes, which agents use when they name add-ons in delegate briefs.

### Changed

- Refined the starting model profiles, bounded mechanical delegation, and approval rules for premium models and substitutions.
- Defined independent review tiers, critical task closure checks, optional scoped consultations and usage evidence in task records.
