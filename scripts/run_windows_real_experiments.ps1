param(
    [string]$InstancesDir = "data/real_routes",
    [int]$Runs = 10,
    [int]$Warmups = 0,
    [string]$Output = "results_real",
    [ValidateSet("variable", "full_tank_only", "both")]
    [string]$PurchaseModel = "both"
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

Write-Host "Running correctness tests..."
uv run pytest -q

Write-Host "Running real-route experiments..."
uv run python scripts/run_real_experiments.py `
    --instances-dir $InstancesDir `
    --runs $Runs `
    --warmups $Warmups `
    --output $Output `
    --purchase-model $PurchaseModel

Write-Host "Finished. Results are in: $Output\real_route_results.csv"
