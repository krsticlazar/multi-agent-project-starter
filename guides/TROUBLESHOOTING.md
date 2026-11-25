# Troubleshooting

## The installer kept an existing path

Review the existing path and compare it with the file under the extracted `template/`. Merge required Bootstrap references or provider settings deliberately. If a file blocks a template directory or a template path points to a link, the installer skips that path. Resolve the collision before relying on that part of the template.

Use the real filesystem path if PowerShell reports a linked destination. Both installers require the destination's parent directory to exist.

If PowerShell blocks a downloaded script, review the source and follow your organization's execution policy. On an unmanaged system where the downloaded-file marker is the cause, you can unblock just the verified `scripts/install.ps1` file with `Unblock-File -LiteralPath .\scripts\install.ps1`. Git Bash is another Windows install path. [PowerShell execution policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)

## Bootstrap could not open Director

Start a new session in the same project root and paste the handoff prompt Bootstrap printed. If the provider exposes a session ID, register the actual identifier. If it exposes neither an ID nor a link, record the handoff and use the role prompt on return. Use native resume only for the correct saved session and avoid concurrent writers into it. [Communication workflow](../template/docs/COMMUNICATION.md)

If the native Windows sandbox blocks the Bootstrap session's filesystem commands, check the current client and its permission profile. Continue in a supported project session with authorized workspace access. Keep the pending handoff until that session can read and update the project files. [Codex Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)

## A CLI session does not appear in the desktop app

Confirm the client, account and workspace, project directory, and OS runtime. A saved session ID can be valid even when the client does not show it in the current sidebar. Use the native CLI session list or resume mechanism in the same environment. [Verification results](VERIFICATION.md) · [Communication workflow](../template/docs/COMMUNICATION.md)

## A turn stopped, a handoff failed, or a provider hit a limit

Check the assigned task and local runtime status. A terminal task report needs an explicit outcome and evidence. Keep the pending report and checkpoint, then send it only once when the destination becomes available. If a subscription limit triggered a pause, checkpoint ongoing work and wait for explicit approval before resuming. [Project workflow](../template/docs/WORKFLOW.md) · [Communication workflow](../template/docs/COMMUNICATION.md)

For a Codex wake, verify the native daemon with `codex app-server daemon version` and check the exact thread's history. `QUEUED` proves acceptance by Codex. `delivered_at` in the local relay proves receipt of the envelope. When the target wakes but its shell cannot run `receive`, bring it back through a supported client with workspace access and recover the pending envelope by its existing ID. Repeated queue submission can create extra turns. [Automatic Codex delivery](../template/docs/COMMUNICATION.md#automatic-codex-delivery)

## Runtime state appears in `git status`

Check `git ls-files -- .runtime` for tracked paths. For an ignored probe file, `git check-ignore -v -- .runtime/probe.txt` shows the matching rule. Keep `/.runtime/` in the root `.gitignore` or the runtime's internal ignore rule when setup uses one. If runtime files are already tracked, resolve that index state with the project owner before writing session data. Git ignore rules do not protect files already in the index.

## Native settings, models, or agents are missing

Check that the session is rooted at the installed directory and that the native client trusts that project when prompted. Inspect installer collisions and restart a session when the client requires it. Use the provider's model picker to verify current access. Then update the project profile after an approved change. [Models](MODELS.md) · [Plugins and skills](PLUGINS.md)
