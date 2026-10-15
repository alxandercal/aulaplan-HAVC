/** Ejecuta Flask usando apps/api/.venv en Windows/macOS sin activar manualmente. */
import { existsSync } from 'node:fs'
import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const executable = process.platform === 'win32'
  ? path.join(root, 'apps', 'api', '.venv', 'Scripts', 'python.exe')
  : path.join(root, 'apps', 'api', '.venv', 'bin', 'python')
if (!existsSync(executable)) {
  console.error('Falta .venv: sigue docs/INSTALACION.md (paso 4).')
  process.exit(1)
}
const child = spawn(executable, ['scripts/run_api.py'], { cwd: root, stdio: 'inherit' })
child.on('error', error => { console.error(error.message); process.exitCode = 1 })
child.on('exit', code => { process.exitCode = code ?? 1 })
