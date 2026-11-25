param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateNotNullOrEmpty()]
    [string]$Destination
)

$ErrorActionPreference = 'Stop'

function Assert-UnlinkedDirectories($Directory) {
    for ($item = $Directory; $item; $item = $item.Parent) {
        if ($item.Exists -and ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            throw "Use the real directory path instead of a linked directory: $($item.FullName)"
        }
    }
}

$source = Get-Item -LiteralPath (Join-Path $PSScriptRoot '../template') -Force
if (!$source.PSIsContainer) {
    throw 'Extract the template into a real directory before installing.'
}
Assert-UnlinkedDirectories $source
$sourceRoot = $source.FullName
$provider = $null
$drive = $null
$destinationPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination, [ref]$provider, [ref]$drive)
if ($provider.Name -ne 'FileSystem') {
    throw 'Choose a filesystem destination.'
}
$destinationPath = [System.IO.Path]::GetFullPath($destinationPath)
$trimmedDestination = $destinationPath.TrimEnd('\', '/')
$separator = [System.IO.Path]::DirectorySeparatorChar

if (($trimmedDestination + $separator).StartsWith(($sourceRoot + $separator), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Choose a destination outside the template directory.'
}

$root = Get-Item -LiteralPath $destinationPath -Force -ErrorAction SilentlyContinue
if ($root -and (!$root.PSIsContainer -or ($root.Attributes -band [System.IO.FileAttributes]::ReparsePoint))) {
    throw "Destination must be a directory, without a link at its root: $destinationPath"
}
$parent = if ($root) { $root.Parent } else { [System.IO.Directory]::GetParent($trimmedDestination) }
Assert-UnlinkedDirectories $parent
if (!$root) {
    if (!$parent -or !$parent.Exists) {
        throw "Destination parent directory does not exist: $parent"
    }
    [void][System.IO.Directory]::CreateDirectory($destinationPath)
}

function Install-TemplateTree($SourceDirectory, $TargetDirectory, $Prefix) {
    foreach ($entry in Get-ChildItem -LiteralPath $SourceDirectory -Force) {
        $relative = $Prefix + $entry.Name
        if ($entry.Name -in '.git', '.runtime', '__pycache__', '.env' -or `
            $entry.Name -like '.env.*' -or $entry.Extension -in '.key', '.pem' -or `
            $relative -eq '.claude/settings.local.json') {
            continue
        }
        $target = Join-Path $TargetDirectory $entry.Name
        $existing = Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
        if ($entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            Write-Output "Skipped source link $relative"
        }
        elseif ($existing -and (!$entry.PSIsContainer -or !$existing.PSIsContainer -or `
            ($existing.Attributes -band [System.IO.FileAttributes]::ReparsePoint))) {
            Write-Output "Kept existing $relative"
        }
        elseif ($entry.PSIsContainer) {
            [void][System.IO.Directory]::CreateDirectory($target)
            Install-TemplateTree $entry.FullName $target "$relative/"
        }
        else {
            [System.IO.File]::Copy($entry.FullName, $target, $false)
            Write-Output "Installed $relative"
        }
    }
}

Install-TemplateTree $sourceRoot $destinationPath ''
Write-Output "Installation finished in $destinationPath. Review any kept paths before running ASK_ME.md."
