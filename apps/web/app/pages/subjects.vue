<script setup lang="ts">
import type { CatalogField } from '~/types'

const fields: CatalogField[] = [
  { key: 'code', label: 'Código', type: 'text', required: true },
  { key: 'name', label: 'Nombre', type: 'text', required: true },
  { key: 'weekly_blocks', label: 'Bloques/semana', type: 'number', required: true },
  { key: 'required_room_type', label: 'Tipo de salón', type: 'select', options: [{ label: 'Aula', value: 'CLASSROOM' }, { label: 'Laboratorio', value: 'LAB' }, { label: 'Sala de cómputo', value: 'COMPUTER_LAB' }], required: true },
  { key: 'active', label: 'Activo', type: 'checkbox', required: false, defaultValue: true }
]
</script>

<template>
  <CatalogManager title="Materias" endpoint="/subjects" :fields="fields" />
</template>