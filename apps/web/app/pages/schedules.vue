<script setup lang="ts">
import type { CatalogRecord, ScheduleVersion } from '~/types'
const { request } = useApi()
const auth = useAuthStore()
const rows = ref<ScheduleVersion[]>([])
const periods = ref<CatalogRecord[]>([])
const selected = ref<ScheduleVersion | null>(null)
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)
const busyId = ref('')
async function load() {
  loading.value = true
  try {
    const [schedules, periodList] = await Promise.all([
      request<ScheduleVersion[]>('/schedules'), request<CatalogRecord[]>('/academic-periods'),
    ])
    rows.value = schedules
    periods.value = periodList
    if (selected.value) selected.value = rows.value.find(row => row.id === selected.value?.id) || null
  } catch (error) { errorMessage.value = readableError(error) }
  finally { loading.value = false }
}
function periodName(id: string) { return String(periods.value.find(p => p.id === id)?.name || id) }
async function publish(id: string) {
  if (!window.confirm('¿Publicar esta versión? Se archivará la versión publicada anterior.')) return
  busyId.value = id
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await request(`/schedules/${id}/publish`, { method: 'POST' })
    await load()
    successMessage.value = 'Horario publicado correctamente.'
  } catch (error) { errorMessage.value = readableError(error) }
  finally { busyId.value = '' }
}
onMounted(load)
</script>
<template>
  <section class="space-y-6">
    <div><h1 class="text-3xl font-bold">Versiones de horarios</h1><p class="opacity-60">Visualización y publicación controlada por periodo académico.</p></div>
    <div v-if="errorMessage" class="alert alert-error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div class="overflow-x-auto rounded-box border border-base-300 bg-base-100">
      <table class="table table-zebra"><thead><tr><th>Versión</th><th>Periodo</th><th>Estado</th><th>Sesiones</th><th>Score</th><th>Acciones</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="6">Cargando…</td></tr>
          <tr v-else-if="rows.length === 0"><td colspan="6">Todavía no existen horarios.</td></tr>
          <tr v-for="row in rows" :key="row.id"><td>v{{ row.version }}</td><td>{{ periodName(row.academic_period_id) }}</td>
            <td><span class="badge" :class="row.status === 'PUBLISHED' ? 'badge-success' : 'badge-ghost'">{{ row.status }}</span></td>
            <td>{{ row.entries.length }}</td><td>{{ row.score }}</td><td class="space-x-2 whitespace-nowrap">
              <button class="btn btn-xs btn-outline" @click="selected = row">Ver sesiones</button>
              <button v-if="row.status === 'DRAFT' && auth.role !== 'VIEWER'" class="btn btn-xs btn-primary" :disabled="busyId === row.id" @click="publish(row.id)">Publicar</button>
            </td></tr>
        </tbody></table>
    </div>
    <div v-if="selected" class="card border border-base-300 bg-base-100"><div class="card-body">
      <div class="flex justify-between gap-4"><h2 class="card-title">Detalle · versión {{ selected.version }}</h2><button class="btn btn-sm" @click="selected = null">Cerrar</button></div>
      <div class="overflow-x-auto"><table class="table table-sm"><thead><tr><th>Día</th><th>Horario</th><th>Grupo</th><th>Materia</th><th>Profesor</th><th>Salón</th></tr></thead>
        <tbody><tr v-for="(e, i) in selected.entries" :key="i"><td>{{ e.day }}</td><td>{{ e.start_time }}–{{ e.end_time }}</td><td>{{ e.group_name }}</td><td>{{ e.subject_name }}</td><td>{{ e.teacher_name }}</td><td>{{ e.room_name }}</td></tr></tbody></table>
      </div>
    </div></div>
  </section>
</template>
