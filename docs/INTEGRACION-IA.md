# Integración de IA — siguiente y única etapa de integración externa

El sistema **funciona sin IA**. El backend reserva `POST /ai/constraints/parse` y responde `501 AI_NOT_CONFIGURED` para no aparentar una integración que no existe. La página de restricciones lo indica explícitamente.

## Objetivo

Permitir que una coordinación académica escriba, por ejemplo, “Andrea no puede los lunes” y que un LLM proponga un objeto `ConstraintCreate` **sin guardar automáticamente** la interpretación. El usuario revisa, confirma y persiste mediante `POST /constraints`. El algoritmo Python continúa siendo la autoridad única para verificar conflictos.

## Arquitectura propuesta

```text
UI textarea -> /ai/constraints/parse -> AIService (provider abstraction)
  -> LLM -> JSON controlado -> Pydantic -> resolucion de IDs
  -> preview explicito -> confirmacion humana -> POST /constraints
  -> POST /schedules/generate -> solver determinista
```

## Archivos a crear o modificar

1. `apps/api/src/services/ai/provider.py`: interfaz `ConstraintParser`.
2. `apps/api/src/services/ai/gemini.py`: implementación con SDK oficial de Gemini, secretos en backend.
3. `apps/api/src/schemas/ai.py`: entrada/salida y validaciones Pydantic.
4. `apps/api/src/http/routes_ai.py`: sustituir el stub 501 por la llamada al servicio.
5. `apps/web/app/pages/constraints.vue`: recuperar textarea, preview de cambios y confirmación antes de almacenar.
6. `apps/api/tests/test_ai_constraints.py`: mocks de proveedor, JSON mal formado, prompt injection, cuotas y fallas.

## Contrato propuesto (aún no implementado)

```http
POST /ai/constraints/parse
Authorization: Bearer <firebase-id-token>
Content-Type: application/json

{"text":"Andrea no puede dar clases los lunes","academic_period_id":"2026-B"}
```

**Propuesta de respuesta**, nunca un CRUD implícito:

```json
{
  "status": "REQUIRES_CONFIRMATION",
  "candidates": [
    {
      "type": "TEACHER_UNAVAILABLE",
      "priority": "HARD",
      "target_type": "TEACHER",
      "target_id": "DOC-001",
      "params": { "day": "MONDAY" },
      "weight": 0,
      "active": true
    }
  ],
  "warnings": [],
  "persisted": false
}
```

## Seguridad y costos

- Nunca exponer keys LLM en `NUXT_PUBLIC_*` ni en el código cliente.
- Autenticar y autorizar cada invocación: `ADMIN` o `COORDINATOR`.
- Evitar incluir datos personales innecesarios en prompts.
- Tratar el texto del usuario y la salida del modelo como no confiables.
- Validación Pydantic de tipo, prioridad, IDs existentes, días y parámetros.
- Requerir confirmación humana; no permitir que el LLM escriba en Firestore ni ejecute código.
- Establecer límites de longitud, tokens, timeout, cuotas por usuario y alertas de gasto.
- Separar errores de proveedor de errores de validación; permitir que el sistema sin IA siga funcionando.

## Definición de terminado para esta etapa

La UI presenta un preview, la API retorna estructuras válidas, el usuario confirma, el constraint se guarda mediante endpoint existente, el scheduler lo aplica como regla HARD/SOFT y las pruebas cubren entrada maliciosa, fallos externos y no regresión del planificador.
