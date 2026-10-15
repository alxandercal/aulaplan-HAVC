<script setup lang="ts">
import type { CatalogRecord, ScheduleVersion } from '~/types'
const { request } = useApi()
const counts = reactive({ teachers: 0, subjects: 0, groups: 0, schedules: 0 })
const loading = ref(true)
const errorMessage = ref('')
onMounted(async () => {
  try {
    const [teachers, subjects, groups, schedules] = await Promise.all([
      request<CatalogRecord[]>('/teachers'), request<CatalogRecord[]>('/subjects'),
      request<CatalogRecord[]>('/groups'), request<ScheduleVersion[]>('/schedules'),
    ])
    Object.assign(counts, {
      teachers: teachers.length, subjects: subjects.length,
      groups: groups.length, schedules: schedules.length,
    })
  } catch (error) { errorMessage.value = readableError(error) }
  finally { loading.value = false }
})
const cards = computed(() => [
  { title: 'Profesores', value: counts.teachers, description: 'Registrados' },
  { title: 'Materias', value: counts.subjects, description: 'Plan académico' },
  { title: 'Grupos', value: counts.groups, description: 'Grupos registrados' },
  { title: 'Horarios', value: counts.schedules, description: 'Versiones generadas' },
])
</script>
<template>
  <section class="space-y-6">
    <header><h1 class="text-3xl font-bold">Dashboard</h1><p class="opacity-60">Resumen académico en tiempo real.</p></header>
    <div v-if="errorMessage" class="alert alert-error">{{ errorMessage }} — verifica API y perfil.</div>
    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard v-for="card in cards" :key="card.title" :title="card.title" :value="loading ? '…' : card.value" :description="card.description" />
    </div>
    <div class="card border border-base-300 bg-base-100">
      <div class="card-body">
        <h2 class="card-title">Flujo de uso</h2>
        <ol class="list-decimal space-y-2 pl-6">
          <li>Capturar el periodo y después profesores, materias, grupos, salones y bloques.</li>
          <li>Crear las ofertas, disponibilidad docente y restricciones.</li>
          <li>Generar horario determinista con cero colisiones obligatorias.</li>
          <li>Revisar sesiones y publicar una versión por periodo.</li>
          <li>En etapa futura: interpretar restricciones en lenguaje natural con IA.</li>
        </ol>
        <div class="card-actions justify-end"><NuxtLink to="/generator" class="btn btn-primary">Ir al generador</NuxtLink></div>
      </div>
    </div>
  </section>
</template>
