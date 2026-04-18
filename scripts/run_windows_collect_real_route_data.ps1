param(
    [string]$Config = "data/real_routes/corridors.example.json",
    [string]$OutputDir = "data/real_routes/generated",
    [string]$RawDir = "data/real_routes/raw",
    [string]$StationPriceCsv = "",
    [string]$InstanceId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not installed or not on PATH. Install it first from https://docs.astral.sh/uv/ or run: winget install astral-sh.uv"
}

Write-Host "Project root: $ProjectRoot"
Write-Host "Ensuring Python 3.11 is available through uv..."
uv python install 3.11

Write-Host "Creating/updating .venv..."
uv venv --python 3.11

Write-Host "Installing project dependencies..."
uv pip install -r requirements.txt -e .

$ArgsList = @(
    "scripts/collect_real_route_data.py",
    "--config", $Config,
    "--output-dir", $OutputDir,
    "--raw-dir", $RawDir
)

if ($StationPriceCsv -ne "") {
    $ArgsList += @("--station-price-csv", $StationPriceCsv)
}

if ($InstanceId -ne "") {
    $ArgsList += @("--instance-id", $InstanceId)
}

Write-Host "Collecting OSM route and fuel-station data..."
uv run python @ArgsList

Write-Host "Finished. Generated instances are in: $OutputDir"
