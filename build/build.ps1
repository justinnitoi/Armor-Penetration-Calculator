<#
  build.ps1

  Compiles every *.py under res\scripts\client\gui\mods and
  res\scripts\client\APCalculator with Python 2.7 (bytecode is version-locked
  -- the WoT client cannot load Python 3 bytecode) and deploys pademinune's
  Armor Penetration Calculator as LOOSE res_mods override files, plus the
  Gameface web assets and res_map registration. Does NOT package a .wotmod --
  see package.ps1 for that.

  Run this from anywhere -- paths are resolved relative to this script, not the
  working directory. Close World of Tanks first -- a running client locks files
  under its install directory.

  Usage:
    .\build.ps1
    .\build.ps1 -Version 2.3.1.2 -WotRoot "D:\Games\World_of_Tanks_NA"
#>

param(
    [string]$WotRoot = "C:\Program Files\World_of_Tanks_NA",
    [string]$Version = "2.3.1.1",
    [string]$Python27 = "python27"   # must be Python 2.7 and on PATH
)

$ErrorActionPreference = "Stop"

# --- paths -----------------------------------------------------------------------
$SourceRoot = Join-Path $PSScriptRoot "..\src"

$PyModsSrcDir         = Join-Path $SourceRoot "res\scripts\client\gui\mods"
$PyAPCalculatorSrcDir = Join-Path $SourceRoot "res\scripts\client\APCalculator"
$WebSrcDir            = Join-Path $SourceRoot "res\gui\gameface\mods\pademinune\APCalculator"
$ResMapSrc            = Join-Path $SourceRoot "res\mods\configs\res_map\APBattleView.json"

$PyDestDir             = Join-Path $WotRoot "res_mods\$Version\scripts\client\gui\mods"
$PyAPCalculatorDestDir = Join-Path $WotRoot "res_mods\$Version\scripts\client\APCalculator"
$WebDestDir            = Join-Path $WotRoot "res_mods\$Version\gui\gameface\mods\pademinune\APCalculator"
$ResMapDestDir         = Join-Path $WotRoot "mods\configs\res_map"

# --- helpers -----------------------------------------------------------------------
function Ensure-Dir($path) {
    if (Test-Path $path) { return }
    try {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    } catch {
        throw "Could not create '$path' -- try re-running PowerShell as Administrator " +
              "('Program Files' is write-protected). $($_.Exception.Message)"
    }
}

function Copy-One($src, $destDir, $label) {
    Ensure-Dir $destDir
    try {
        Copy-Item -Path $src -Destination $destDir -Force
        Write-Host "  copied: $label"
    } catch {
        throw "Failed to copy $label into '$destDir' -- is WorldOfTanks.exe running " +
              "(file lock), or do you need Administrator rights? $($_.Exception.Message)"
    }
}

# Compiles every *.py under $srcDir -- including subfolders, e.g. a settings_gui
# sub-package -- with Python 2.7 and moves each resulting .pyc into $destDir at
# the same relative subpath, clearing any stale .py/.pyc sibling first (a stale
# sibling of either kind can shadow the fresh file and silently run old code).
function Invoke-PyCompile($srcDir, $destDir) {
    $srcDirFull = (Resolve-Path $srcDir).Path.TrimEnd('\')
    $modules = Get-ChildItem -Path $srcDir -Filter "*.py" -Recurse
    if ($modules.Count -eq 0) {
        throw "No .py files found in '$srcDir'"
    }

    foreach ($module in $modules) {
        $relPath = $module.FullName.Substring($srcDirFull.Length + 1)
        $relSubDir = Split-Path $relPath -Parent
        $moduleDestDir = if ($relSubDir) { Join-Path $destDir $relSubDir } else { $destDir }

        Write-Host "Compiling $relPath ..."
        & $Python27 -m py_compile $module.FullName
        if ($LASTEXITCODE -ne 0) {
            throw "py_compile failed on $relPath (exit $LASTEXITCODE). Check '$Python27' is Python 2.7 and on PATH."
        }

        $compiled = [System.IO.Path]::ChangeExtension($module.FullName, ".pyc")
        if (-not (Test-Path $compiled)) {
            throw "Expected compiled output not found: $compiled"
        }

        Ensure-Dir $moduleDestDir

        foreach ($ext in @(".py", ".pyc")) {
            $stale = Join-Path $moduleDestDir ([System.IO.Path]::ChangeExtension($module.Name, $ext))
            if (Test-Path $stale) {
                Remove-Item $stale -Force
                Write-Host "  removed stale: $(Split-Path $stale -Leaf)"
            }
        }

        try {
            Move-Item -Path $compiled -Destination $moduleDestDir -Force
            Write-Host "  moved: $($module.BaseName).pyc -> $moduleDestDir"
        } catch {
            throw "Failed to move the compiled .pyc -- is WorldOfTanks.exe running? $($_.Exception.Message)"
        }
    }
}

# --- 0. sanity + elevation hint -----------------------------------------------------
if (-not (Test-Path $WotRoot)) {
    throw "WoT install not found: $WotRoot (pass -WotRoot to override)"
}
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Not running as Administrator -- writes under 'Program Files' may fail."
}

# --- 1. compile every Python module -------------------------------------------------
Invoke-PyCompile $PyModsSrcDir $PyDestDir
Invoke-PyCompile $PyAPCalculatorSrcDir $PyAPCalculatorDestDir

# --- 2. copy the Gameface web assets ------------------------------------------------
Write-Host "Copying gameface assets ..."
Get-ChildItem -Path $WebSrcDir -File | ForEach-Object {
    Copy-One $_.FullName $WebDestDir $_.Name
}

# --- 3. copy the res_map registration -----------------------------------------------
Write-Host "Copying res_map entry ..."
Copy-One $ResMapSrc $ResMapDestDir "APBattleView.json"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "First-ever deploy: restart the WoT client so OpenWG picks up the res_map entry." -ForegroundColor Green
Write-Host "After that: JS/CSS/Python edits just need this script re-run + a new battle" -ForegroundColor Green
Write-Host "(restart the client too if a change doesn't seem to take effect)." -ForegroundColor Green
