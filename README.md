# AulaPlan — Monorepo completo sin IA

**Frontend:** Nuxt 4 + Vue 3 + TypeScript + Pinia + Tailwind CSS + DaisyUI.  
**Backend:** Python 3.11 + Flask + Pydantic + Firebase Admin SDK.  
**Autenticación y BD:** Firebase Authentication / Cloud Firestore (emuladores locales).  
**Motor de horarios:** búsqueda determinista con validación de reglas HARD.

El ZIP se distribuye sin `node_modules` ni el lockfile antiguo: **`npm install` genera el nuevo `package-lock.json`**.

Esta entrega completa las rutas que faltaban de generación/listado/publicación de horarios, el formulario de catálogos, la administración de usuarios, el bootstrap de emuladores y las pruebas del scheduler. **La interpretación con IA queda reservada para una etapa posterior:** `/ai/constraints/parse` responde 501 a propósito.

## Primera ejecución (desde raíz)

1. Instalar Node 24 LTS, Python 3.11 y JDK 21; instalar Firebase CLI: `npm install -g firebase-tools`.
2. Instalar frontend: `npm install`.
3. Crear entorno Python: `python3.11 -m venv apps/api/.venv` (Windows: `py -3.11 -m venv apps/api/.venv`).
4. Activar entorno, instalar Python: `python -m pip install -r apps/api/requirements.txt`.
5. Copiar `.env.example` a `.env` en `apps/api` y `apps/web`.
6. Abrir tres terminales y ejecutar `npm run dev:firebase`, `python scripts/run_api.py` (con entorno Python activado) y `npm run dev:web`. Alternativa: **`npm run dev`** para levantar los tres servicios juntos después de instalar `.venv`.
7. Crear admin: `python apps/api/scripts/create_admin.py --email admin@example.test --name Administrador` (contraseña interactiva) y después `python apps/api/scripts/seed_demo.py`.
8. Iniciar sesión en `http://localhost:3000`, generar horario y publicarlo.

## Documentos

- **[Instalación completa, Mac/Windows y despliegue](docs/INSTALACION.md)**
- **[Arquitectura, endpoints y reglas de negocio](docs/ARQUITECTURA.md)**
- **[Punto de integración de IA pendiente](docs/INTEGRACION-IA.md)**

## Pruebas

```bash
python -m pytest apps/api/tests -q
npm run typecheck:web
npm run generate:web
```

`python` debe señalar a `apps/api/.venv` activado. Las pruebas del solver no requieren un proyecto Firebase; pruebas E2E de Auth/Firestore requieren emuladores en ejecución.

## Seguridad

No hay secretos predeterminados ni cuentas de producción incluidas. El archivo `firestore.rules` cierra el acceso directo por defecto. Todas las operaciones de datos pasan por API autenticada y RBAC. Para Cloud Functions, ejecutar `npm run prepare:functions` antes de `firebase deploy`. Evite sustituir el proyecto demo por un proyecto real sin revisar primero las variables y las reglas de producción.
