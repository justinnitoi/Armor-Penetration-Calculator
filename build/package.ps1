<#
  package.ps1

  Compiles every *.py under src\res\scripts\client\gui\mods and
  src\res\scripts\client\ap_calculator with Python 2.7 -- the same compile step
  build.ps1 uses -- then stages the result plus the Gameface web assets, the
  settings-tooltip icons, the translation files, the res_map registration, and
  meta.xml under bin\, and zips it all into a .wotmod package (ZIP_STORED,
  meta.xml at the archive root, everything else under res\). Unlike build.ps1
  this does NOT touch a WoT install -- it only produces bin\wotmods\<name>.wotmod.

  The staging directory is wiped before every run so a package never mixes
  freshly compiled output with leftovers from a previous src layout.

  Run this from anywhere -- paths are resolved relative to this script, not the
  working directory.

  Usage:
    .\package.ps1
    .\package.ps1 -Python27 "C:\Python27\python.exe"
#>

param(
    [string]$Python27 = "python27"   # must be Python 2.7 and on PATH
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

# --- paths -----------------------------------------------------------------------
$SourceRoot = Join-Path $PSScriptRoot "..\src"
$BinDir     = Join-Path $PSScriptRoot "..\bin"
$StageDir   = Join-Path $BinDir "package"
$ResDir     = Join-Path $StageDir "res"
$OutDir     = Join-Path $BinDir "wotmods"

$PyModsSrcDir         = Join-Path $SourceRoot "res\scripts\client\gui\mods"
$PyApCalculatorSrcDir = Join-Path $SourceRoot "res\scripts\client\ap_calculator"
$WebSrcDir            = Join-Path $SourceRoot "res\gui\AP_Calculator_2\gameface"
$IconsSrcDir          = Join-Path $SourceRoot "res\gui\AP_Calculator_2\tooltips"
$TranslationsSrcDir   = Join-Path $SourceRoot "res\gui\AP_Calculator_2\translations"
$ResMapSrc            = Join-Path $SourceRoot "res\mods\configs\res_map\APBattleView.json"
$MetaSrc              = Join-Path $SourceRoot "meta.xml"

$PyModsDestDir         = Join-Path $ResDir "scripts\client\gui\mods"
$PyApCalculatorDestDir = Join-Path $ResDir "scripts\client\ap_calculator"
$WebDestDir            = Join-Path $ResDir "gui\AP_Calculator_2\gameface"
$IconsDestDir          = Join-Path $ResDir "gui\AP_Calculator_2\tooltips"
$TranslationsDestDir   = Join-Path $ResDir "gui\AP_Calculator_2\translations"
$ResMapDestDir         = Join-Path $ResDir "mods\configs\res_map"

# Mod version comes from meta.xml so the package name can't drift out of sync
# with what actually ships inside it.
$ModVersion = ([xml](Get-Content $MetaSrc)).root.version
$MOD_NAME   = "pademinune-armor-pen-calc-$ModVersion"
$OutFile    = Join-Path $OutDir "$MOD_NAME.wotmod"

# --- helpers -----------------------------------------------------------------------
function Ensure-Dir($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Force -Path $path | Out-Null }
}

# Compiles every *.py under $srcDir -- including subfolders, e.g. a settings_gui
# sub-package -- with Python 2.7 and copies each resulting .pyc into $destDir at
# the same relative subpath. Same shape as build.ps1's Invoke-PyCompile, but
# copies rather than moves the compiled output, since the staging dir (not the
# src tree) is what gets wiped and rebuilt each run.
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
        Copy-Item -Path $compiled -Destination $moduleDestDir -Force
        Remove-Item $compiled -Force
        Write-Host "  staged: $($module.BaseName).pyc -> $moduleDestDir"
    }
}

# --- 0. wipe stale staging output ---------------------------------------------------
if (Test-Path $StageDir) { Remove-Item $StageDir -Recurse -Force }
Ensure-Dir $ResDir
Ensure-Dir $OutDir

# --- 1. compile every Python module -------------------------------------------------
Invoke-PyCompile $PyModsSrcDir $PyModsDestDir
Invoke-PyCompile $PyApCalculatorSrcDir $PyApCalculatorDestDir

# --- 2. copy the Gameface web assets ------------------------------------------------
Write-Host "Copying gameface assets ..."
Ensure-Dir $WebDestDir
Get-ChildItem -Path $WebSrcDir -File | ForEach-Object {
    Copy-Item $_.FullName -Destination $WebDestDir -Force
}

# --- 3. copy the settings-tooltip icons ----------------------------------------------
Write-Host "Copying settings-tooltip icons ..."
Ensure-Dir $IconsDestDir
Get-ChildItem -Path $IconsSrcDir -File | ForEach-Object {
    Copy-Item $_.FullName -Destination $IconsDestDir -Force
}

# --- 4. copy the localization files ---------------------------------------------------
Write-Host "Copying translation files ..."
Ensure-Dir $TranslationsDestDir
Get-ChildItem -Path $TranslationsSrcDir -File | ForEach-Object {
    Copy-Item $_.FullName -Destination $TranslationsDestDir -Force
}

# --- 5. copy the res_map registration -----------------------------------------------
Write-Host "Copying res_map entry ..."
Ensure-Dir $ResMapDestDir
Copy-Item $ResMapSrc -Destination $ResMapDestDir -Force

# --- 6. copy meta.xml (archive root, alongside res\, not inside it) -----------------
Copy-Item $MetaSrc -Destination $StageDir -Force

# --- 7. zip the staging dir into the .wotmod package ---------------------------------
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }

# includeBaseDirectory=false: entries come out as "res\..." and "meta.xml" at the
# zip root, not wrapped in a "package\" folder.
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $StageDir,
    $OutFile,
    [System.IO.Compression.CompressionLevel]::NoCompression,
    $false
)

Write-Output "Packaged: $OutFile"
