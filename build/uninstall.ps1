<#
  uninstall.ps1

  Removes the loose res_mods override files that build.ps1 deploys: compiled
  .pyc modules, the Gameface web assets, the settings-tooltip icons, the
  translation files, and the res_map registration. Derives the same paths from
  the same source tree as build.ps1, so it always matches whatever build.ps1
  last put there instead of a hardcoded file list going stale.

  Run this from anywhere -- paths are resolved relative to this script, not the
  working directory. Close World of Tanks first -- a running client locks files
  under its install directory.

  Usage:
    .\uninstall.ps1
    .\uninstall.ps1 -Version 2.3.1.2 -WotRoot "D:\Games\World_of_Tanks_NA"
#>

param(
    [string]$WotRoot = "C:\Program Files\World_of_Tanks_NA",
    [string]$Version = "2.4.0.0"
)

$ErrorActionPreference = "Stop"

# --- paths -----------------------------------------------------------------------
$SourceRoot = Join-Path $PSScriptRoot "..\src"

$PyModsSrcDir         = Join-Path $SourceRoot "res\scripts\client\gui\mods"
$PyApCalculatorSrcDir = Join-Path $SourceRoot "res\scripts\client\ap_calculator"
$WebSrcDir            = Join-Path $SourceRoot "res\gui\AP_Calculator_2\gameface"
$IconsSrcDir          = Join-Path $SourceRoot "res\gui\AP_Calculator_2\tooltips"
$TranslationsSrcDir   = Join-Path $SourceRoot "res\gui\AP_Calculator_2\translations"

$PyDestDir             = Join-Path $WotRoot "res_mods\$Version\scripts\client\gui\mods"
$PyApCalculatorDestDir = Join-Path $WotRoot "res_mods\$Version\scripts\client\ap_calculator"
$WebDestDir            = Join-Path $WotRoot "res_mods\$Version\gui\AP_Calculator_2\gameface"
$IconsDestDir          = Join-Path $WotRoot "res_mods\$Version\gui\AP_Calculator_2\tooltips"
$TranslationsDestDir   = Join-Path $WotRoot "res_mods\$Version\gui\AP_Calculator_2\translations"
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

# Removes the compiled .pyc for every *.py under $srcDir -- including
# subfolders, e.g. a settings_gui sub-package -- from $destDir at the same
# relative subpath, then prunes any subdirectories left empty by that (deepest
# first, so a chain of now-empty parents is fully cleaned up too).
function Remove-CompiledPyDir($srcDir, $destDir) {
    $modules = Get-ChildItem -Path $srcDir -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
    if ($modules.Count -gt 0) {
        $srcDirFull = (Resolve-Path $srcDir).Path.TrimEnd('\')
        foreach ($module in $modules) {
            $relPath = $module.FullName.Substring($srcDirFull.Length + 1)
            $relSubDir = Split-Path $relPath -Parent
            $moduleDestDir = if ($relSubDir) { Join-Path $destDir $relSubDir } else { $destDir }
            $pycName = [System.IO.Path]::ChangeExtension($module.Name, ".pyc")
            $label = if ($relSubDir) { Join-Path $relSubDir $pycName } else { $pycName }
            Remove-IfExists (Join-Path $moduleDestDir $pycName) $label
        }
    }

    if (-not (Test-Path $destDir)) { return }
    Get-ChildItem -Path $destDir -Recurse -Directory |
        Sort-Object { $_.FullName.Length } -Descending |
        ForEach-Object {
            if ((Get-ChildItem $_.FullName -Force | Measure-Object).Count -eq 0) {
                Remove-Item $_.FullName -Force
                Write-Host "  removed empty directory: $($_.FullName)"
            }
        }
    if ((Get-ChildItem $destDir -Force | Measure-Object).Count -eq 0) {
        Remove-Item $destDir -Force
        Write-Host "  removed empty directory: $destDir"
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

Write-Host "Removing compiled ap_calculator package ..."
Remove-CompiledPyDir $PyApCalculatorSrcDir $PyApCalculatorDestDir

# --- 2. remove the Gameface web assets ------------------------------------------------
Write-Host "Removing gameface assets ..."
Get-ChildItem -Path $WebSrcDir -File -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-IfExists (Join-Path $WebDestDir $_.Name) $_.Name
}
if ((Test-Path $WebDestDir) -and ((Get-ChildItem $WebDestDir -Force | Measure-Object).Count -eq 0)) {
    Remove-Item $WebDestDir -Force
    Write-Host "  removed empty directory: $WebDestDir"
}

# --- 3. remove the settings-tooltip icons ----------------------------------------------
Write-Host "Removing settings-tooltip icons ..."
Get-ChildItem -Path $IconsSrcDir -File -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-IfExists (Join-Path $IconsDestDir $_.Name) $_.Name
}
if ((Test-Path $IconsDestDir) -and ((Get-ChildItem $IconsDestDir -Force | Measure-Object).Count -eq 0)) {
    Remove-Item $IconsDestDir -Force
    Write-Host "  removed empty directory: $IconsDestDir"
}

# --- 4. remove the translation files ---------------------------------------------------
Write-Host "Removing translation files ..."
Get-ChildItem -Path $TranslationsSrcDir -File -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-IfExists (Join-Path $TranslationsDestDir $_.Name) $_.Name
}
if ((Test-Path $TranslationsDestDir) -and ((Get-ChildItem $TranslationsDestDir -Force | Measure-Object).Count -eq 0)) {
    Remove-Item $TranslationsDestDir -Force
    Write-Host "  removed empty directory: $TranslationsDestDir"
}

# --- 5. remove the res_map registration -----------------------------------------------
Write-Host "Removing res_map entry ..."
Remove-IfExists (Join-Path $ResMapDestDir "APBattleView.json") "APBattleView.json"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
