param(
    [string]$SyntheticInput = "results/synthetic_results.csv",
    [string]$RealInput = "real_route_results.csv",
    [string]$RealInstancesDir = "data/real_routes/generated",
    [string]$ReportDir = "final-report-revised"
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

Write-Host "Generating synthetic report assets..."
.venv\Scripts\python.exe scripts/analyze_synthetic_results.py --input $SyntheticInput --output-dir results/report_assets

Write-Host "Generating real-route report assets..."
.venv\Scripts\python.exe scripts/analyze_real_results.py --input $RealInput --instances-dir $RealInstancesDir --output-dir results/report_assets/exp6_real_routes

Push-Location $ReportDir
try {
    Write-Host "Building final report PDF..."
    pdflatex -interaction=nonstopmode final-report.tex
    biber final-report
    pdflatex -interaction=nonstopmode final-report.tex
    pdflatex -interaction=nonstopmode final-report.tex
}
finally {
    Pop-Location
}

Write-Host "Finished. Final PDF: $ReportDir\\final-report.pdf"
