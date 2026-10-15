<script setup lang="ts">
import type { CatalogField, CatalogRecord } from '~/types'
const props = defineProps<{ title: string; endpoint: string; fields: CatalogField[] }>()
const auth = useAuthStore()
const canEdit = computed(() => ['ADMIN', 'COORDINATOR'].includes(auth.role ?? ''))
const { request } = useApi()
const rows = ref<CatalogRecord[]>([])
// eslint-disable-next-line @typescript-eslint/no-explicit-any -- valores heterogeneos ligados con v-model
const form = reactive<Record<string, any>>({})
const optionsByReference = reactive<Record<string, Array<{ label: string; value: string }>>>({})
const editingId = ref<string | null>(null)
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

function resetForm() {
  editingId.value = null
  for (const key of Object.keys(form)) delete form[key]
  for (const field of props.fields) {
    form[field.key] = field.defaultValue ?? (field.type === 'checkbox' ? true : field.type === 'number' ? 0 : field.type === 'json' ? '{}' : '')
  }
}
function displayValue(row: CatalogRecord, field: CatalogField): string {
  const value = row[field.key]
  if (field.type === 'checkbox') return value ? 'Sí' : 'No'
  if (field.reference) return optionsByReference[field.reference]?.find(x => x.value === value)?.label || String(value ?? '')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value ?? '')
}
function choices(field: CatalogField) {
  return field.reference ? optionsByReference[field.reference] || [] : field.options || []
}
async function loadReferences() {
  const references = [...new Set(props.fields.map(f => f.reference).filter((s): s is string => Boolean(s)))]
  await Promise.all(references.map(async (endpoint) => {
    const records = await request<CatalogRecord[]>(endpoint)
    optionsByReference[endpoint] = records.map(row => ({
      label: String(row.name || row.code || row.day || row.id) + (row.code && row.name ? ` (${row.code})` : ''),
      value: row.id,
    }))
  }))
}
async function load() {
  loading.value = true
  errorMessage.value = ''
  try { rows.value = await request<CatalogRecord[]>(props.endpoint) }
  catch (error) { errorMessage.value = readableError(error) }
  finally { loading.value = false }
}
function edit(row: CatalogRecord) {
  editingId.value = row.id
  for (const field of props.fields) {
    form[field.key] = field.type === 'json' ? JSON.stringify(row[field.key] ?? {}, null, 2) : row[field.key]
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
async function save() {
  if (!canEdit.value) return
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const body: Record<string, unknown> = {}
    for (const field of props.fields) {
      const value = form[field.key]
      body[field.key] = field.type === 'number' ? Number(value) : field.type === 'json' ? JSON.parse(String(value || '{}')) : value
    }
    await request(editingId.value ? `${props.endpoint}/${editingId.value}` : props.endpoint, {
      method: editingId.value ? 'PUT' : 'POST', body,
    })
    resetForm()
    await load()
    await loadReferences()
    successMessage.value = 'Registro guardado correctamente.'
  } catch (error) { errorMessage.value = readableError(error) }
  finally { saving.value = false }
}
async function remove(id: string) {
  if (!canEdit.value || !window.confirm('¿Eliminar este registro?')) return
  errorMessage.value = ''
  try { await request(`${props.endpoint}/${id}`, { method: 'DELETE' }); await load() }
  catch (error) { errorMessage.value = readableError(error) }
}
onMounted(async () => {
  resetForm()
  try { await loadReferences() } catch (error) { errorMessage.value = readableError(error) }
  await load()
})
</script>
<template>
  <section class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">{{ title }}</h1>
      <p class="text-sm opacity-60">Gestión académica conectada al backend Python.</p>
    </div>
    <div v-if="errorMessage" role="alert" class="alert alert-error">{{ errorMessage }}</div>
    <div v-if="successMessage" role="status" class="alert alert-success">{{ successMessage }}</div>
    <form v-if="canEdit" class="card border border-base-300 bg-base-100" @submit.prevent="save">
      <div class="card-body grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <label v-for="field in fields" :key="field.key" class="form-control">
          <span class="label-text mb-1">{{ field.label }}</span>
          <select v-if="field.type === 'select' || field.reference" v-model="form[field.key]" class="select select-bordered w-full" :required="field.required">
            <option value="">Selecciona una opción</option>
            <option v-for="option in choices(field)" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
          <input v-else-if="field.type === 'checkbox'" v-model="form[field.key]" type="checkbox" class="toggle toggle-primary" />
          <textarea v-else-if="field.type === 'json'" v-model="form[field.key]" class="textarea textarea-bordered font-mono" rows="3" />
          <input v-else v-model="form[field.key]" :type="field.type || 'text'" class="input input-bordered w-full" :required="field.required" />
        </label>
        <div class="flex gap-2 md:col-span-2 xl:col-span-3">
          <button class="btn btn-primary" type="submit" :disabled="saving">{{ saving ? 'Guardando…' : editingId ? 'Actualizar' : 'Guardar' }}</button>
          <button v-if="editingId" class="btn" type="button" @click="resetForm">Cancelar</button>
        </div>
      </div>
    </form>
    <div class="overflow-x-auto rounded-box border border-base-300 bg-base-100">
      <table class="table table-zebra">
        <thead><tr><th v-for="field in fields" :key="field.key">{{ field.label }}</th><th v-if="canEdit">Acciones</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td :colspan="fields.length + (canEdit ? 1 : 0)">Cargando…</td></tr>
          <tr v-else-if="rows.length === 0"><td :colspan="fields.length + (canEdit ? 1 : 0)">Sin registros. Agrega el primero.</td></tr>
          <tr v-for="row in rows" :key="row.id">
            <td v-for="field in fields" :key="field.key" class="max-w-52 truncate" :title="displayValue(row, field)">{{ displayValue(row, field) }}</td>
            <td v-if="canEdit" class="whitespace-nowrap">
              <button class="btn btn-xs mr-2" @click="edit(row)">Editar</button>
              <button class="btn btn-xs btn-error btn-outline" @click="remove(row.id)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
