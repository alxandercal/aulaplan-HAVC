<script setup lang="ts">
import type { CatalogField } from '~/types'

const fields: CatalogField[] = [
  { key: 'teacher_id', reference: '/teachers', label: 'ID profesor', type: 'text', required: true },
  { key: 'time_block_id', reference: '/time-blocks', label: 'ID bloque', type: 'text', required: true },
  { key: 'available', label: 'Disponible', type: 'checkbox', required: false, defaultValue: true },
  { key: 'preference_weight', label: 'Preferencia', type: 'number', required: false }
]
</script>

<template>
  <CatalogManager title="Disponibilidad docente" endpoint="/availability" :fields="fields" />
</template>