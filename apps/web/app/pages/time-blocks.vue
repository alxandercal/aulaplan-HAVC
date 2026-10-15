<script setup lang="ts">
import type { CatalogField } from '~/types'

const fields: CatalogField[] = [
  { key: 'day', label: 'Día', type: 'select', options: [{ label: 'Lunes', value: 'MONDAY' }, { label: 'Martes', value: 'TUESDAY' }, { label: 'Miércoles', value: 'WEDNESDAY' }, { label: 'Jueves', value: 'THURSDAY' }, { label: 'Viernes', value: 'FRIDAY' }, { label: 'Sábado', value: 'SATURDAY' }], required: true },
  { key: 'start_time', label: 'Inicio', type: 'text', required: true },
  { key: 'end_time', label: 'Fin', type: 'text', required: true },
  { key: 'order', label: 'Orden', type: 'number', required: true },
  { key: 'active', label: 'Activo', type: 'checkbox', required: false, defaultValue: true }
]
</script>

<template>
  <CatalogManager title="Bloques horarios" endpoint="/time-blocks" :fields="fields" />
</template>