# AulaPlan — Guía de instalación completa (macOS y Windows)

**Edición:** octubre 2026 · **Objetivo:** tener gestión académica, usuarios, generación de horarios y publicación de versiones funcionales **sin integrar todavía IA**.

> **Importante:** el proyecto está preparado para ejecutarse con emuladores locales, sin un proyecto real de Firebase y sin una API key de Gemini. El ZIP excluye `node_modules`, entornos virtuales, credenciales y el archivo `.env` privado del proyecto auditado. Se instalan dependencias desde cero.

## 1. Requisitos

| Herramienta | Versión recomendada | Uso |
|---|---|---|
| Node.js | 24 LTS (mínimo 22 para este proyecto) | Nuxt 4, npm y Firebase CLI |
| Python | **3.11.x** | Flask, Admin SDK y Cloud Functions Python 3.11 |
| Git | Versión estable | Control de versiones |
| Java | JDK 21 | Emulador de Firestore |
| Firebase CLI | Versión estable | Emuladores y despliegue |
| VS Code | Opcional | Desarrollo |

**macOS (Terminal):**

```bash
# Instalar Homebrew si no está disponible: https://brew.sh/
brew install node@24 python@3.11 openjdk@21 git

# Si Homebrew no vinculó Java o Node a tu PATH, revisa las instrucciones
# que imprime `brew info openjdk@21` y `brew info node@24`.
node --version
npm --version
python3.11 --version
java -version
npm install -g firebase-tools
firebase --version
```

**Windows 11 (PowerShell; abrir de nuevo la terminal después de instalar):**

```powershell
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.11
winget install EclipseAdoptium.Temurin.21.JDK
winget install Git.Git

node --version
npm --version
py -3.11 --version
java -version
npm install -g firebase-tools
firebase --version
```

Si en Windows PowerShell la política impide ejecutar `npm.ps1`, puede usar `npm.cmd` o ajustar la política de ejecución **solo para CurrentUser** según las políticas de su equipo. No ejecute scripts remotos sin revisarlos.

## 2. Extraer el ZIP y ubicarse en la raíz

Descomprima `AulaPlan-Completo-Sin-IA.zip`. La **raíz** contiene `package.json`, `firebase.json`, `apps/`, `scripts/` y `docs/`.

**macOS:**

```bash
cd ~/Desktop/aulaplan-mars
pwd
ls
```

**Windows (PowerShell):**

```powershell
cd "$HOME\Desktop\aulaplan-mars"
Get-Location
Get-ChildItem
```

> Si descomprimió en otra ubicación, cambie `cd` a la carpeta real. No ejecute comandos de la raíz desde `apps/web` o `apps/api` salvo cuando se indique.

### Instalación asistida opcional

Los scripts `scripts/setup_mac.sh` y `scripts/setup_windows.ps1` automatizan los pasos 3 a 5 **después de instalar los requisitos del paso 1**. No modifican `.env` existente. Si prefiere comprender cada instalación, siga los pasos manuales a continuación.

**macOS (desde raíz):** `bash scripts/setup_mac.sh`.  
**Windows PowerShell (desde raíz):** `powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1` únicamente después de inspeccionar el contenido del script incluido.

## 3. Instalar las dependencias del frontend

Desde la **raíz del monorepo** y con internet:

```bash
npm install
```

Esto instala Nuxt 4, Vue 3, Pinia, Tailwind CSS 4, DaisyUI, Firebase SDK, TypeScript y Vue TSC. El ZIP no incluye el `package-lock.json` antiguo debido a inconsistencias detectadas en las dependencias originales; **`npm install` generará uno nuevo y coherente**. Después de comprobarlo, agréguelo a Git para instalaciones reproducibles. **No copie** el antiguo `node_modules` del ZIP auditado.

Si su instalación limpia queda inconsistente, elimine **solo** `node_modules` y regenere dependencias con `npm install`. No elimine sus archivos de trabajo ni `.env`.

## 4. Crear y activar el entorno Python

**macOS (en la raíz):**

```bash
python3.11 -m venv apps/api/.venv
source apps/api/.venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -r apps/api/requirements.txt
```

**Windows PowerShell (en la raíz):**

```powershell
py -3.11 -m venv apps/api/.venv
.\apps\api\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r apps/api/requirements.txt
```

**Alternativa Windows CMD:** `apps\api\.venv\Scripts\activate.bat`.

La terminal activada mostrará `(.venv)`. Para salir, ejecute `deactivate`.

> **Nota:** El backend fue programado para Python 3.11, como en Firebase Functions. No use el Python 3.13 global del equipo cuando tenga activado `.venv`.

## 5. Configurar las variables de entorno

Para desarrollo local, los valores de ejemplo ya apuntan al proyecto ficticio `demo-aulaplan` y a los emuladores.

**macOS (raíz):**

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

**Windows PowerShell (raíz):**

```powershell
Copy-Item apps/api/.env.example apps/api/.env
Copy-Item apps/web/.env.example apps/web/.env
```

**Backend:** `apps/api/.env` contiene `FIREBASE_PROJECT_ID=demo-aulaplan`, `FIRESTORE_EMULATOR_HOST=127.0.0.1:8080`, `FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099`, `API_PORT=8000` y los orígenes CORS.

**Frontend:** `apps/web/.env` apunta a `http://127.0.0.1:8000`, activa los emuladores y declara la configuración Firebase *ficticia* para desarrollo. Estas variables `NUXT_PUBLIC_*` son **públicas**; nunca coloque en ellas claves privadas del Admin SDK ni claves de IA.

## 6. Levantar los servicios: **tres terminales independientes**

<details>
<summary>Terminal 1: emuladores Auth y Firestore</summary>

Desde la raíz:

```bash
npm run dev:firebase
```

Iniciará Auth en `127.0.0.1:9099`, Firestore en `127.0.0.1:8080` y la consola de emuladores normalmente en `http://127.0.0.1:4000`. El script importa datos existentes y los exporta al cerrar para conservarlos en `.firebase/emulator-data`.

La primera ejecución puede descargar binarios de los emuladores y requiere internet. **Deje esta terminal abierta.**
</details>

<details>
<summary>Terminal 2: backend Python Flask</summary>

Abra una segunda terminal en la raíz. Active el entorno Python:

**macOS:**

```bash
source apps/api/.venv/bin/activate
python scripts/run_api.py
```

**Windows PowerShell:**

```powershell
.\apps\api\.venv\Scripts\Activate.ps1
python scripts/run_api.py
```

Prueba sin autenticación: abra `http://127.0.0.1:8000/health`. Debe ver `{"status":"ok","service":"aulaplan-api","runtime":"python"}`. **Deje la terminal abierta.**
</details>

<details>
<summary>Terminal 3: frontend Nuxt 4</summary>

Abra una tercera terminal en la raíz:

```bash
npm run dev:web
```

Abra `http://localhost:3000` (o la URL anunciada por Nuxt). **Deje la terminal abierta.**
</details>

**No es necesario arrancar el emulador de Functions** para desarrollo local: Flask se ejecuta directamente en puerto 8000, y el frontend consume sus endpoints REST.

### Alternativa: arrancar los tres servicios con un comando

Después de configurar dependencias y `.env` (pasos 1–5), puede usar **una sola terminal** en la raíz:

```bash
npm run dev
```

Este comando ejecuta simultáneamente los emuladores, Flask con `apps/api/.venv` y Nuxt. Para depuración en clase se recomiendan las tres terminales separadas porque permiten ver los logs de cada servicio con más claridad.

## 7. Crear el administrador local y cargar datos demo

Abra una **cuarta terminal** en la raíz, con el entorno Python activado (paso 4) y los emuladores activos. Reutilice la contraseña de su elección: no hay credenciales predeterminadas ni contraseñas en el repositorio.

```bash
python apps/api/scripts/create_admin.py --email admin@example.test --name Administrador
```

Escriba la contraseña cuando se solicite (mínimo ocho caracteres). La entrada no se mostrará en pantalla.

Luego cargue los catálogos:

```bash
python apps/api/scripts/seed_demo.py
```

Se crean, sin duplicados: periodo `2026-B`, dos profesores, tres materias, dos grupos, cuatro salones, 20 bloques, cuatro ofertas y dos disponibilidades. Las ofertas suman **10 sesiones semanales**.

**Compruebe:** inicie sesión con `admin@example.test` y la contraseña elegida. Acceda a Dashboard, luego a Generador; seleccione el periodo Agosto-Diciembre 2026 y pulse **Generar horario**. En Horarios puede inspeccionar las sesiones y **Publicar**.

## 8. Verificación y pruebas

En otra terminal con `.venv` activo, desde la raíz:

```bash
npm run test:api
npm run typecheck:web
npm run generate:web
```

Para probar la API de salud:

**macOS:**

```bash
curl http://127.0.0.1:8000/health
```

**Windows PowerShell:**

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

**Verificación funcional manual:** admin inicia sesión; consulta catálogos; crea/edita profesores, materias, grupos y ofertas; genera una versión sin conflictos; publica; segundo horario publicado archiva el primero; VIEWER no puede modificar ni publicar; las reglas Firestore niegan el acceso directo desde el navegador.

## 9. Diagnóstico de errores frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: src.http.app` | Ejecutar un script desde ruta incorrecta | Desde la raíz use `python scripts/run_api.py` |
| `ModuleNotFoundError: flask` | `.venv` no activado o pip no instalado | Active `.venv` y ejecute `python -m pip install -r apps/api/requirements.txt` |
| `Could not reach Cloud Firestore backend` | Emulador Firestore apagado | Mantenga terminal 1 activa, revise puerto 8080 |
| Java no encontrado | JDK ausente en PATH | Instale JDK 21 y reinicie terminal |
| `401 UNAUTHENTICATED` | Token inválido / proyecto distinto | Revise el mismo `demo-aulaplan` en API, web y emuladores |
| `403 PROFILE_NOT_FOUND` | Usuario creado en Auth pero no en Firestore | Ejecute `create_admin.py` con los emuladores activos |
| `422 INVALID_REFERENCE` | ID de profesor/grupo/etc. inexistente | Use menús desplegables o cargue demo primero |
| `422 SCHEDULE_UNFEASIBLE` | Restricciones incompatibles con bloques/salones | Revise disponibilidad, carga y restricciones |
| `501 AI_NOT_CONFIGURED` | Función de IA pendiente por diseño | Consulte `docs/INTEGRACION-IA.md` |
| `npm` o Nuxt falla después de copiar el antiguo ZIP | Dependencias `node_modules` obsoletas | No copie `node_modules`; ejecute `npm install` limpio |
| CORS del backend | Frontend corre en otra URL | Añada la URL exacta a `CORS_ORIGINS` y reinicie Flask |
| Puerto ocupado | Otra app usa 3000/8000/8080/9099 | Detenga procesos duplicados o ajuste configuración coherentemente |

## 10. Preparación para Firebase/Netlify reales (opcional)

El desarrollo local funciona **sin costo de despliegue**, usando únicamente emuladores. Para una publicación real:

1. Cree/seleccione un **proyecto real** desde [Firebase Console](https://console.firebase.google.com/) y habilite **Authentication (Email/Password)** y **Cloud Firestore**.
2. El despliegue de Cloud Functions requiere la facturación/plan de Firebase adecuado (habitualmente Blaze), además de los permisos de Google Cloud pertinentes.
3. Configure el frontend en Netlify con los valores reales `NUXT_PUBLIC_FIREBASE_*`, `NUXT_PUBLIC_USE_FIREBASE_EMULATORS=false` y `NUXT_PUBLIC_API_BASE_URL=https://us-central1-PROJECT_ID.cloudfunctions.net/api`. **No use localhost en producción.**
4. En `functions/.env.PROJECT_ID`, configure `CORS_ORIGINS=https://SU_SITIO.netlify.app` (copie el archivo `.env.example` como base).
5. Para desplegar desde la raíz (sustituya el ID real y revise que sea el correcto):

```bash
firebase login
firebase use --add
npm run prepare:functions
firebase deploy --only functions,firestore
```

6. En Netlify: base directory `apps/web`, build command `npm run generate` y publish directory `.output/public` (relativo a `apps/web`). También puede usar el flujo de integración con Git; configure las variables en el entorno de Netlify antes del build.
7. Para ADMIN de producción: cree el usuario en **Firebase Authentication** por consola; copie su UID y cree por **Firestore Console** `users/{UID}` con `email`, `display_name`, `role: "ADMIN"`, `active: true`. El script `create_admin.py` está bloqueado deliberadamente fuera de emuladores.
8. Verifique autenticación, CRUD, generación y publicación en su ambiente de pruebas antes de exponer el sitio a usuarios reales.

**No publique archivos `serviceAccount*.json`, secretos, `.env` de backend ni exportaciones de emuladores.** Las reglas Firestore incluidas deniegan accesos directos: todas las operaciones pasan por un backend autenticado y autorizado.

## 11. Qué falta exclusivamente para IA

- Implementar el adaptador en `apps/api/src/services/ai/` (por ejemplo Gemini a través del SDK del proveedor).
- Resolver una credencial de IA solo en backend (Firebase Functions secrets o variables de entorno seguras).
- Implementar `POST /ai/constraints/parse` sustituyendo el `501` por salida estructurada Pydantic, validación y confirmación del usuario.
- Agregar pruebas de prompts, seguridad, límites de costo, manejo de fallos y revisión humana.

**El generador de horarios NO necesita IA.** Ya está implementado en `apps/api/src/services/scheduler.py`. Para el contrato propuesto, lea `docs/INTEGRACION-IA.md`.
