# Downloads a GitHub source archive of the starter and runs its scripts/install.ps1.
# Usage: & ([scriptblock]::Create((irm <raw url of this file>))) -Destination 'C:\Projects\my-app' [-Ref <full commit hash>]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateNotNullOrEmpty()]
    [string]$Destination,
    [ValidatePattern('^(main|[a-fA-F0-9]{40})$')]
    [string]$Ref = 'main'
)

$ErrorActionPreference = 'Stop'
$repository = 'multi-agent-project-starter'
# Resolve against the PowerShell location, which a child process does not inherit.
$target = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)
$scratch = Join-Path ([IO.Path]::GetTempPath()) "$repository-$([guid]::NewGuid())"
[void][IO.Directory]::CreateDirectory($scratch)
try {
    $archive = Join-Path $scratch 'starter.zip'
    Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/krsticlazar/$repository/archive/$Ref.zip" -OutFile $archive
    Expand-Archive -LiteralPath $archive -DestinationPath (Join-Path $scratch 'source')
    # GitHub names the single archive root after the requested ref.
    $roots = @(Get-ChildItem -LiteralPath (Join-Path $scratch 'source') -Force)
    $installer = Join-Path $scratch "source/$repository-$Ref/scripts/install.ps1"
    if ($roots.Count -ne 1 -or $roots[0].Name -ne "$repository-$Ref" -or !(Test-Path -LiteralPath $installer -PathType Leaf)) {
        throw "Unexpected starter archive layout for ref $Ref."
    }
    # A child process keeps the existing installer unchanged; Bypass applies to that process only.
    $shell = Join-Path $PSHOME $(if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' })
    & $shell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $installer -Destination $target
    if ($LASTEXITCODE -ne 0) {
        throw "Installer exited with code $LASTEXITCODE."
    }
}
finally {
    Remove-Item -LiteralPath $scratch -Recurse -Force -ErrorAction SilentlyContinue
}
