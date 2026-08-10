<#
  uninstall.ps1

  Removes the loose res_mods override files that build.ps1 deploys: compiled
  .pyc modules, the Gameface web assets, and the res_map registration. Derives
  the same paths from the same source tree as build.ps1, so it always matches
  whatever build.ps1 last put there instead of a hardcoded file list going stale.

  Run this from anywhere -- paths are resolved relative to this script, not the
  working directory. Close World of Tanks first -- a running client locks files
  under its install directory.

  Usage:
    .\uninstall.ps1
    .\uninstall.ps1 -Version 2.3.1.2 -WotRoot "D:\Games\World_of_Tanks_NA"
#>

param(
    [string]$WotRoot = "C:\Program Files\World_of_Tanks_NA",
    [string]$Version = "2.3.1.1"
)

$ErrorActionPreference = "Stop"

# --- paths -----------------------------------------------------------------------
$SourceRoot = Join-Path $PSScriptRoot "..\src"

$PyModsSrcDir         = Join-Path $SourceRoot "res\scripts\client\gui\mods"
$PyAPCalculatorSrcDir = Join-Path $SourceRoot "res\scripts\client\APCalculator"
$WebSrcDir            = Join-Path $SourceRoot "res\gui\gameface\mods\pademinune\APCalculator"

$PyDestDir             = Join-Path $WotRoot "res_mods\$Version\scripts\client\gui\mods"
$PyAPCalculatorDestDir = Join-Path $WotRoot "res_mods\$Version\scripts\client\APCalculator"
$WebDestDir            = Join-Path $WotRoot "res_mods\$Version\gui\gameface\mods\pademinune\APCalculator"
$ResMapDestDir         = Join-Path $WotRoot "mods\configs\res_map"

# --- helper -----------------------------------------------------------------------
function Remove-IfExists($path, $label) {
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "  removed: $label"
    } else {
        Write-Host "  skipped (not present): $label"
    }
}

# --- 0. sanity + elevation hint -----------------------------------------------------
if (-not (Test-Path $WotRoot)) {
    throw "WoT install not found: $WotRoot (pass -WotRoot to override)"
}
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Not running as Administrator -- removals under 'Program Files' may fail."
}

# --- 1. remove compiled Python modules -----------------------------------------------
Write-Host "Removing compiled Python modules ..."
$PyModules = Get-ChildItem -Path $PyModsSrcDir -Filter "*.py" -ErrorAction SilentlyContinue
foreach ($module in $PyModules) {
    $pycName = [System.IO.Path]::ChangeExtension($module.Name, ".pyc")
    Remove-IfExists (Join-Path $PyDestDir $pycName) $pycName
}

Write-Host "Removing compiled APCalculator package ..."
$PyAPCalculatorModules = Get-ChildItem -Path $PyAPCalculatorSrcDir -Filter "*.py" -ErrorAction SilentlyContinue
foreach ($module in $PyAPCalculatorModules) {
    $pycName = [System.IO.Path]::ChangeExtension($module.Name, ".pyc")
    Remove-IfExists (Join-Path $PyAPCalculatorDestDir $pycName) $pycName
}
if ((Test-Path $PyAPCalculatorDestDir) -and ((Get-ChildItem $PyAPCalculatorDestDir -Force | Measure-Object).Count -eq 0)) {
    Remove-Item $PyAPCalculatorDestDir -Force
    Write-Host "  removed empty directory: $PyAPCalculatorDestDir"
}

# --- 2. remove the Gameface web assets ------------------------------------------------
Write-Host "Removing gameface assets ..."
Get-ChildItem -Path $WebSrcDir -File -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-IfExists (Join-Path $WebDestDir $_.Name) $_.Name
}
if ((Test-Path $WebDestDir) -and ((Get-ChildItem $WebDestDir -Force | Measure-Object).Count -eq 0)) {
    Remove-Item $WebDestDir -Force
    Write-Host "  removed empty directory: $WebDestDir"
}

# --- 3. remove the res_map registration -----------------------------------------------
Write-Host "Removing res_map entry ..."
Remove-IfExists (Join-Path $ResMapDestDir "APBattleView.json") "APBattleView.json"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
