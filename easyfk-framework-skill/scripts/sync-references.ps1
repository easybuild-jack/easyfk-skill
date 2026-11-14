<#
  Build or refresh the reference snapshot of one easyfk version.

  versions/<Version>/modules/  module skill docs. The snapshot is the only copy and is edited in place;
                               this script never overwrites it. With -From, a new version starts from
                               a copy of versions/<From>/modules/.
  versions/<Version>/manuals/  <- every path listed in versions/<Version>/manuals.txt, copied from RepoRoot
                                  (original relative layout kept, so links between manuals keep working)

  RepoRoot must be the source tree of exactly that version (e.g. a checkout of its git tag).
  An existing manuals/ is never overwritten unless -Force is given, because manuals may carry
  hand edits recorded in VERSION.md.

  Usage:
    powershell -ExecutionPolicy Bypass -File <skill dir>/scripts/sync-references.ps1 -Version 3.5.16 -From 3.2.12 -RepoRoot D:\codespace\framework\easyfk_3.5.16
    powershell -ExecutionPolicy Bypass -File <skill dir>/scripts/sync-references.ps1 -Version 3.2.12 -RepoRoot D:\codespace\framework\easyfk_3.2.12 -Force
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$From,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$skillDir = Split-Path -Parent $PSScriptRoot
$versionsDir = Join-Path $skillDir 'versions'
$versionDir = Join-Path $versionsDir $Version
$modulesDir = Join-Path $versionDir 'modules'
$manualsDir = Join-Path $versionDir 'manuals'
$manifest = Join-Path $versionDir 'manuals.txt'

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    Write-Error "RepoRoot not found: $RepoRoot"
}

if ($From) {
    $fromDir = Join-Path $versionsDir $From
    if (-not (Test-Path -LiteralPath $fromDir)) {
        Write-Error "snapshot $From not found: $fromDir"
    }
    if (-not (Test-Path -LiteralPath $versionDir)) { New-Item -ItemType Directory -Path $versionDir | Out-Null }
    if (Test-Path -LiteralPath $modulesDir) {
        Write-Host "modules: already exists, kept"
    } else {
        Copy-Item -LiteralPath (Join-Path $fromDir 'modules') -Destination $modulesDir -Recurse
        Write-Host ("modules: copied from {0}" -f $From)
    }
    if (-not (Test-Path -LiteralPath $manifest)) {
        Copy-Item -LiteralPath (Join-Path $fromDir 'manuals.txt') -Destination $manifest
        Write-Host ("manuals.txt: copied from {0}, adjust it if this version adds or removes manuals" -f $From)
    }
}

if (-not (Test-Path -LiteralPath $manifest)) {
    Write-Error "manifest not found: $manifest (use -From <previous version>, or copy the previous manuals.txt first)"
}
if (-not (Test-Path -LiteralPath $modulesDir)) {
    Write-Warning "modules/ not found for $Version; use -From <previous version> to start from the previous snapshot"
}

if ((Test-Path -LiteralPath $manualsDir) -and -not $Force) {
    Write-Error "manuals of $Version already exist; rerun with -Force to overwrite manuals/"
}
if (Test-Path -LiteralPath $manualsDir) { Remove-Item -LiteralPath $manualsDir -Recurse -Force }
New-Item -ItemType Directory -Path $manualsDir | Out-Null

$missing = @()
$copied = 0
foreach ($line in (Get-Content -Path $manifest -Encoding UTF8)) {
    $rel = $line.Trim()
    if ($rel -eq '' -or $rel.StartsWith('#')) { continue }
    $src = Join-Path $RepoRoot $rel
    if (-not (Test-Path -LiteralPath $src)) { $missing += $rel; continue }
    $dst = Join-Path $manualsDir $rel
    $dstParent = Split-Path -Parent $dst
    if (-not (Test-Path -LiteralPath $dstParent)) { New-Item -ItemType Directory -Path $dstParent -Force | Out-Null }
    Copy-Item -LiteralPath $src -Destination $dst -Force
    $copied++
}
Write-Host ("manuals: {0} files" -f $copied)
if ($missing.Count -gt 0) {
    Write-Warning ("missing {0} manuals:" -f $missing.Count)
    $missing | ForEach-Object { Write-Warning "  $_" }
    exit 1
}
