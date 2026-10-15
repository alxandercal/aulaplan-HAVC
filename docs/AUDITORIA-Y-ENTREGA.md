# Auditoría y entrega — AulaPlan sin IA

## Hallazgos al inspeccionar `aulaplan-mars-auditoria.zip`

1. Las pantallas `/schedules`, `/schedules/generate` y `/schedules/{id}/publish` se conectaban a endpoints ausentes en Flask.
2. `/ai/constraints/parse` estaba referenciado desde la UI, pero el backend carecía de endpoint.
3. La configuración del proyecto contenía un esqueleto distinto de Cloud Functions al backend `apps/api`: el despliegue no empaquetaba sus módulos.
4. Varios archivos `apps/web/app/pages/*.vue` tenían caracteres literales `\\n` dentro de los arreglos TypeScript.
5. El backend local no cargaba los valores de entorno ni inicializaba el Admin SDK en un único punto de entrada.
6. El modelo Pydantic de grupos usaba `academic_period` mientras la interfaz enviaba `academic_period_id`.
7. `ValidationError` se devolvía erróneamente como un `404`, en lugar de `422`.
8. Los formularios Vue enviaban números como strings y solo permitían copiar IDs manualmente.
9. La versión original no incluía un generador determinista, pruebas automatizadas de horarios ni un seed académico integral.
10. El ZIP auditado incluía carpetas `node_modules` y un `.env` privado de frontend, que no deben circular como entrega.

## Correcciones implementadas

- Autenticación Firebase + RBAC `ADMIN`, `COORDINATOR`, `VIEWER`.
- CRUD de catálogos con Pydantic, validación de referencias y errores estructurados.
- Administración de usuarios y bootstrap ADMIN para emuladores.
- Seed idempotente de profesores, salones, grupos, materias, bloques y ofertas.
- Motor determinista de horarios, disponibilidad, preferencias y restricciones.
- Versiones `DRAFT`, publicación transaccional y `ARCHIVED`.
- Dashboard con datos reales, formularios con referencias y visualización de sesiones.
- Scripts multiplataforma de instalación, emuladores con persistencia y arranque simultáneo.
- Cloud Functions preparado para desplegar mediante `npm run prepare:functions`.
- Stub `501 AI_NOT_CONFIGURED` y guía para construir IA sin afectar el scheduler.

## Verificaciones realizadas en este entorno

| Verificación | Resultado |
|---|---|
| Compilación sintáctica Python (`compileall`) | **Correcto** |
| Tests unitarios del scheduler (`pytest`) | **10/10 correctos** |
| Parseo de SFC y templates Vue (22 archivos) | **Sin errores** |
| Parseo de scripts TypeScript con Babel | **Sin errores sintácticos** |
| Sintaxis de scripts Node del proyecto | **Correcta** |
| Frontend `nuxt generate` | **No verificable**: dependencias extraídas del ZIP original eran inconsistentes; sin acceso a registro npm para reinstalación limpia |
| Pruebas E2E con Firebase | **No ejecutadas**: el entorno no tiene instalaciones de Firebase/Flask ni descarga de paquetes |
| Despliegue a Firebase/Netlify | **No ejecutado**: requiere credenciales y proyecto real del usuario |

**Alcance de la afirmación «completo»:** la implementación de las funciones académicas y del motor determinista se entrega en código fuente. Debe completarse la instalación limpia, el typecheck/build y la prueba E2E de la guía antes de considerarla validada para producción. La integración con LLM es un desarrollo futuro intencional, no una funcionalidad simulada.
