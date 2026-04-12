Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

.\scripts\run_windows_synthetic_experiments.ps1 `
    -Profile lite `
    -Runs 100 `
    -Warmups 0 `
    -Output results_synthetic_100 `
    -Seed 42 `
    -Degree 3 `
    -BaseNodes 300 `
    -ScalabilityNodes "100,300,1000"

