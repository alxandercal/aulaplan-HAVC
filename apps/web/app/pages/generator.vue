<script setup lang="ts">
import type { CatalogRecord, ScheduleVersion } from '~/types'
const { request } = useApi()
const auth = useAuthStore()
const periods = ref<CatalogRecord[]>([])
const periodId = ref('')
const maxNodes = ref(50000)
const result = ref<ScheduleVersion | null>(null)
const loading = ref(false)
const errorMessage = ref('')
onMounted(async () => {
  try {
    periods.value = await request<CatalogRecord[]>('/academic-periods')
    const current = periods.value.find(row => row.active)
    if (current) periodId.value = current.id
  } catch (error) { errorMessage.value = readableError(error) }
})
async function generate() {
  loading.value = true
  result.value = null
  errorMessage.value = ''
  try {
    result.value = await request<ScheduleVersion>('/schedules/generate', {
      method: 'POST', body: { academic_period_id: periodId.value, max_nodes: Number(maxNodes.value) },
    })
  } catch (error) { errorMessage.value = readableError(error) }
  finally { loading.value = false }
}
const days: Record<string, string> = {
  MONDAY: 'Lunes', TUESDAY: 'Martes', WEDNESDAY: 'Miércoles',
  THURSDAY: 'Jueves', FRIDAY: 'Viernes', SATURDAY: 'Sábado',
}
</script>
<template>
  <section class="space-y-6">
    <div><h1 class="text-3xl font-bold">Generador de horarios</h1>
      <p class="opacity-60">Motor determinista Python: sin modelos de IA ni claves externas.</p></div>
    <div v-if="errorMessage" role="alert" class="alert alert-error">{{ errorMessage }}</div>
    <div class="card border border-base-300 bg-base-100"><div class="card-body grid gap-4 md:grid-cols-3">
      <label class="form-control"><span class="label-text mb-1">Periodo académico</span>
        <select v-model="periodId" class="select select-bordered w-full" required>
          <option value="">Seleccionar</option>
          <option v-for="period in periods.filter(p => p.active)" :key="period.id" :value="period.id">{{ period.name }} ({{ period.code }})</option>
        </select></label>
      <label class="form-control"><span class="label-text mb-1">Máximo de nodos</span>
        <input v-model.number="maxNodes" type="number" min="100" max="200000" class="input input-bordered w-full" /></label>
      <div class="flex items-end"><button class="btn btn-primary" :disabled="loading || !periodId || auth.role === 'VIEWER'" @click="generate">
        {{ loading ? 'Generando…' : 'Generar horario' }}</button></div>
    </div></div>
    <div v-if="result" class="space-y-4">
      <div class="alert alert-success">Horario versión {{ result.version }} generado correctamente: {{ result.metrics.sessions }} sesiones sin colisiones.</div>
      <div class="flex flex-wrap gap-3 text-sm"><span class="badge badge-outline">Score: {{ result.score }}</span><span class="badge badge-outline">Nodos: {{ result.metrics.explored_nodes }}</span><NuxtLink to="/schedules" class="link link-primary">Ver versiones y publicar</NuxtLink></div>
      <div class="overflow-x-auto rounded-box border border-base-300 bg-base-100">
        <table class="table table-zebra"><thead><tr><th>Día</th><th>Horario</th><th>Grupo</th><th>Materia</th><th>Profesor</th><th>Salón</th></tr></thead>
          <tbody><tr v-for="(entry, i) in result.entries" :key="i"><td>{{ days[entry.day] || entry.day }}</td><td>{{ entry.start_time }}–{{ entry.end_time }}</td><td>{{ entry.group_name }}</td><td>{{ entry.subject_name }}</td><td>{{ entry.teacher_name }}</td><td>{{ entry.room_name }}</td></tr></tbody>
        </table>
      </div>
    </div>
  </section>
</template>
