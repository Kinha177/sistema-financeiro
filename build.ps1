# build.ps1 — Gera o executável do SisGest Financeiro via PyInstaller
#
# Uso:
#   .\build.ps1           # build normal
#   .\build.ps1 -Clean    # limpa dist/ e build/ antes de compilar
#
# Pré-requisito: venv criado e dependências instaladas.
#   python -m venv venv
#   .\venv\Scripts\pip install -r requirements.txt

param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ── limpeza opcional ──────────────────────────────────────────────────────────

if ($Clean) {
    foreach ($dir in @("dist", "build")) {
        if (Test-Path $dir) {
            Write-Host "Removendo $dir..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force $dir
        }
    }
}

# ── verificações ──────────────────────────────────────────────────────────────

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host @"
Virtualenv nao encontrado. Execute:
  python -m venv venv
  .\venv\Scripts\pip install -r requirements.txt
"@ -ForegroundColor Red
    exit 1
}

$python       = "venv\Scripts\python.exe"
$pip          = "venv\Scripts\pip.exe"
$pyinstaller  = "venv\Scripts\pyinstaller.exe"

if (-not (Test-Path $pyinstaller)) {
    Write-Host "Instalando PyInstaller..." -ForegroundColor Cyan
    & $pip install --quiet "PyInstaller>=6.0.0"
}

# ── build ─────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SisGest Financeiro — Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& $pyinstaller sisfinanceiro.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Build falhou. Verifique os erros acima." -ForegroundColor Red
    exit 1
}

# ── resultado ─────────────────────────────────────────────────────────────────

$destino = "dist\SisGestFinanceiro"
$exe     = "$destino\SisGestFinanceiro.exe"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build concluido com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Executavel : $exe" -ForegroundColor White
Write-Host "Pasta      : $destino" -ForegroundColor White

$tamanho = (Get-ChildItem -Recurse $destino | Measure-Object -Property Length -Sum).Sum
$mb = [math]::Round($tamanho / 1MB, 1)
Write-Host "Tamanho    : $mb MB" -ForegroundColor White
Write-Host ""
Write-Host "Para distribuir, compacte a pasta '$destino' em um .zip." -ForegroundColor Gray
