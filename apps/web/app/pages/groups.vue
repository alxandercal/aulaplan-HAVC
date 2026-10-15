<script setup lang="ts">
import type { CatalogField } from '~/types'

const fields: CatalogField[] = [
  { key: 'code', label: 'Código', type: 'text', required: true },
  { key: 'name', label: 'Nombre', type: 'text', required: true },
  { key: 'student_count', label: 'Alumnos', type: 'number', required: true },
  { key: 'academic_period_id', reference: '/academic-periods', label: 'ID periodo', type: 'text', required: true },
  { key: 'active', label: 'Activo', type: 'checkbox', required: false, defaultValue: true }
]
</script>

<template>
  <CatalogManager title="Grupos" endpoint="/groups" :fields="fields" />
</template>