# Windows MSVC Coverage Generator Script
# SPDX-License-Identifier: LGPL-2.1-or-later

$ErrorActionPreference = "Stop"

$root = "C:\Users\Sudhish\Documents\code\dev\FreeCAD"
$openCppCoverage = "C:\Program Files\OpenCppCoverage\OpenCppCoverage.exe"
$outputDir = "$root\coverage_report"

Write-Host "========================================="
Write-Host "Generating C++ Code Coverage on Windows (MSVC)"
Write-Host "========================================="

if (-not (Test-Path $openCppCoverage)) {
    Write-Error "OpenCppCoverage is not installed. Run 'winget install OpenCppCoverage.OpenCppCoverage'."
}

# Run coverage on the core binary and export HTML report
Write-Host "Running coverage for core unit tests (App_tests_run)..."
& $openCppCoverage --sources "$root\src" --export_type="html:$outputDir" -- "$root\build\debug\bin\App_tests_run.exe"

Write-Host "========================================="
Write-Host "Coverage report generated successfully!"
Write-Host "Open $outputDir\index.html in your browser."
Write-Host "========================================="
