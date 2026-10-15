<script setup lang="ts">
import type { CatalogField } from '~/types'
const fields: CatalogField[] = [
  { key: 'type', label: 'Tipo de regla', type: 'select', required: true, options: [
    { label: 'Profesor no disponible', value: 'TEACHER_UNAVAILABLE' },
    { label: 'Salón no disponible', value: 'ROOM_UNAVAILABLE' },
    { label: 'Grupo no disponible', value: 'GROUP_UNAVAILABLE' },
    { label: 'Día preferido del profesor', value: 'TEACHER_PREFERRED_DAY' },
  ] },
  { key: 'priority', label: 'Prioridad', type: 'select', required: true, options: [
    { label: 'Obligatoria (HARD)', value: 'HARD' },
    { label: 'Preferida (SOFT)', value: 'SOFT' },
  ] },
  { key: 'target_type', label: 'Entidad', type: 'select', required: true, options: [
    { label: 'Profesor', value: 'TEACHER' },
    { label: 'Salón', value: 'ROOM' },
    { label: 'Grupo', value: 'GROUP' },
  ] },
  { key: 'target_id', label: 'ID objetivo', required: true },
  { key: 'params', label: 'Parámetros JSON', type: 'json', defaultValue: '{"day":"MONDAY"}' },
  { key: 'weight', label: 'Preferencia (+/-)', type: 'number', defaultValue: 0 },
  { key: 'active', label: 'Activo', type: 'checkbox', defaultValue: true },
]
</script>
<template>
  <section class="space-y-6">
    <div class="alert alert-info block">
      <strong>Restricciones deterministas disponibles.</strong>
      <p class="mt-1 text-sm">Ejemplo de parámetros: <code>{"day":"MONDAY"}</code> o <code>{"time_block_id":"MON-01"}</code>.
        Para el tipo TEACHER_UNAVAILABLE utiliza prioridad HARD y entidad TEACHER.
        Para TEACHER_PREFERRED_DAY utiliza prioridad SOFT. No se aceptan reglas desconocidas.</p>
      <p class="mt-1 text-sm">La interpretación en lenguaje natural con IA es la siguiente fase y no está conectada.</p>
    </div>
    <CatalogManager title="Restricciones" endpoint="/constraints" :fields="fields" />
  </section>
</template>
