param(
    [ValidateSet("smoke", "lite", "proposal")]
    [string]$Profile = "smoke",

    [int]$Runs = 10,

    [int]$Warmups = 0,

    [string]$Output = "results",

    [int]$Seed = 42,

    [int]$Degree = 5,

    [int]$BaseNodes = 0,

    [string]$ScalabilityNodes = ""
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

Write-Host "Running synthetic experiments..."
$ExperimentArgs = @(
    "scripts/run_all_experiments.py",
    "--profile", $Profile,
    "--runs", $Runs,
    "--warmups", $Warmups,
    "--output", $Output,
    "--seed", $Seed,
    "--degree", $Degree
)

if ($BaseNodes -gt 0) {
    $ExperimentArgs += @("--base-nodes", $BaseNodes)
}

if ($ScalabilityNodes -ne "") {
    $ExperimentArgs += @("--scalability-nodes", $ScalabilityNodes)
}

uv run python @ExperimentArgs

Write-Host "Finished. Results are in: $Output\synthetic_results.csv"
