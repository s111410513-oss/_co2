# run_all.ps1 -- regenerate every artefact in this report from scratch
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$ys = Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\Scripts\yowasp-yosys.exe"
if (-not (Test-Path $ys)) {
    Write-Host "Yosys not found - installing via pip ..."
    python -m pip install yowasp-yosys
    $ys = (Get-Command yowasp-yosys -ErrorAction SilentlyContinue).Source
}
if (-not $ys) { throw "yowasp-yosys.exe not found. Run: python -m pip install yowasp-yosys" }

New-Item -ItemType Directory -Force -Path out, log | Out-Null

function Run-Flow($script, $log) {
    Write-Host "==> $script"
    & $ys -l $log $script *> $null
    if ($LASTEXITCODE -ne 0) { throw "Yosys failed: $script (see $log)" }
    Write-Host "    ok  ($log)"
}

Run-Flow "scripts/synth_alu.ys"     "log/alu_synth.log"
Run-Flow "scripts/synth_counter.ys" "log/counter_synth.log"
Run-Flow "scripts/synth_fpga.ys"    "log/fpga.log"
Run-Flow "scripts/verify.ys"        "log/verify.log"
Run-Flow "scripts/lec.ys"           "log/lec.log"

Write-Host "==> figures"
python scripts/make_figures.py

Write-Host ""
Write-Host "All artefacts regenerated in out/ and log/"
