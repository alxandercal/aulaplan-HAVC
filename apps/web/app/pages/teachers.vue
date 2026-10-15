<script setup lang="ts">
import type { CatalogField } from '~/types'

const fields: CatalogField[] = [
  { key: 'code', label: 'Código', type: 'text', required: true },
  { key: 'name', label: 'Nombre', type: 'text', required: true },
  { key: 'email', label: 'Correo', type: 'email', required: true },
  { key: 'max_daily_blocks', label: 'Máx. bloques/día', type: 'number', required: true },
  { key: 'max_weekly_blocks', label: 'Máx. bloques/semana', type: 'number', required: true },
  { key: 'active', label: 'Activo', type: 'checkbox', required: false, defaultValue: true }
]
</script>

<template>
  <CatalogManager title="Profesores" endpoint="/teachers" :fields="fields" />
</template>