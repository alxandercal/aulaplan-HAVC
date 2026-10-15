# Configura dependencias; abrir PowerShell en la raiz. No ejecuta instaladores de sistema.
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
foreach ($cmd in @('node', 'npm.cmd', 'py', 'java', 'firebase.cmd')) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Falta $cmd. Revisa docs/INSTALACION.md, seccion 1."
  }
}
npm.cmd install
if ($LASTEXITCODE -ne 0) { throw 'Fallo npm install' }
py -3.11 -m venv apps/api/.venv
if ($LASTEXITCODE -ne 0) { throw 'Fallo crear .venv' }
& '.\apps\api\.venv\Scripts\python.exe' -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Fallo pip upgrade' }
& '.\apps\api\.venv\Scripts\python.exe' -m pip install -r apps/api/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Fallo pip requirements' }
if (-not (Test-Path 'apps/api/.env')) { Copy-Item 'apps/api/.env.example' 'apps/api/.env' }
if (-not (Test-Path 'apps/web/.env')) { Copy-Item 'apps/web/.env.example' 'apps/web/.env' }
Write-Host 'Instalacion completada. Ver docs/INSTALACION.md secciones 6 y 7.'
