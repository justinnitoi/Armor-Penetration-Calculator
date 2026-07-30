Add-Type -AssemblyName System.IO.Compression.FileSystem

$MOD_NAME = "pademinune-armor-pen-calc-1.8.2"

$BinDir   = "$PSScriptRoot\..\bin"
$ModsDir  = "$BinDir\res\scripts\client\gui\mods"
$ResDir   = "$BinDir\res"
$OutDir   = "$BinDir\wotmods"
$OutFile  = "$OutDir\$MOD_NAME.wotmod"

# Ensure required directories exist
New-Item -ItemType Directory -Force -Path $ModsDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# Copy all .pyc files from bin root into the mods directory
Get-ChildItem -Path $BinDir -Filter "*.pyc" | ForEach-Object {
    Copy-Item $_.FullName -Destination $ModsDir -Force
}

# Remove stale output if it exists
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }

# Zip res\ with no compression (store mode); includeBaseDirectory keeps the res\ prefix
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $ResDir,
    $OutFile,
    [System.IO.Compression.CompressionLevel]::NoCompression,
    $true
)

Write-Output "Packaged: $OutFile"
