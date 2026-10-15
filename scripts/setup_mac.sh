#!/usr/bin/env bash
# Configura dependencias de proyecto; no instala Node/Python/Java en el sistema.
set -euo pipefail
cd "$(dirname "$0")/.."
for cmd in node npm python3.11 java firebase; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Falta $cmd. Ver docs/INSTALACION.md sección 1." >&2
    exit 1
  fi
done
npm install
python3.11 -m venv apps/api/.venv
apps/api/.venv/bin/python -m pip install --upgrade pip
apps/api/.venv/bin/python -m pip install -r apps/api/requirements.txt
[[ -f apps/api/.env ]] || cp apps/api/.env.example apps/api/.env
[[ -f apps/web/.env ]] || cp apps/web/.env.example apps/web/.env
echo 'Instalación completada. Ver docs/INSTALACION.md sección 6 y 7.'
