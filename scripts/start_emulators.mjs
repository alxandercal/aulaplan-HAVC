/** Ejecuta Auth+Firestore emulators y conserva datos entre sesiones. */
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const data = path.join(root, '.firebase', 'emulator-data')
const args = [
  'emulators:start', '--project', 'demo-aulaplan',
  '--only', 'auth,firestore', `--export-on-exit=${data}`,
]
if (existsSync(path.join(data, 'firebase-export-metadata.json'))) args.push(`--import=${data}`)
console.log('Emuladores en proyecto demo-aulaplan; datos persistidos en .firebase/emulator-data')
const isWindows = process.platform === 'win32'
const cli = isWindows ? 'firebase.cmd' : 'firebase'
// En Windows se usa shell: Node une los argumentos con espacios sin comillas,
// asi que una ruta como "C:\Universidad\Cuarto semestre\..." se partiria en dos.
const quote = arg => (/[\s"]/.test(arg) ? `"${arg.replace(/"/g, '\\"')}"` : arg)
const finalArgs = isWindows ? args.map(quote) : args
const child = spawn(cli, finalArgs, { cwd: root, stdio: 'inherit', shell: isWindows })
child.on('error', error => { console.error('Firebase CLI no disponible:', error.message); process.exitCode = 1 })
child.on('exit', code => { process.exitCode = code ?? 1 })
