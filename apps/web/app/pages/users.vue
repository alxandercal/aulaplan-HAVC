<script setup lang="ts">
import type { Role, UserProfile } from '~/types'
const { request } = useApi()
const users = ref<UserProfile[]>([])
const errorMessage = ref('')
const successMessage = ref('')
const busy = ref(false)
const editingId = ref('')
const draft = reactive<{ display_name: string; role: Role; active: boolean }>({ display_name: '', role: 'VIEWER', active: true })
const form = reactive({ email: '', password: '', display_name: '', role: 'VIEWER' as Role })
async function load() {
  try { users.value = await request<UserProfile[]>('/users') }
  catch (error) { errorMessage.value = readableError(error) }
}
async function createUser() {
  busy.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await request('/users', { method: 'POST', body: { ...form } })
    form.email = ''; form.password = ''; form.display_name = ''; form.role = 'VIEWER'
    await load()
    successMessage.value = 'Usuario creado.'
  } catch (error) { errorMessage.value = readableError(error) }
  finally { busy.value = false }
}
function edit(user: UserProfile) {
  editingId.value = user.uid
  Object.assign(draft, { display_name: user.display_name, role: user.role, active: user.active })
}
async function save() {
  busy.value = true
  errorMessage.value = ''
  try {
    await request(`/users/${editingId.value}`, { method: 'PUT', body: { ...draft } })
    editingId.value = ''
    await load()
    successMessage.value = 'Perfil actualizado.'
  } catch (error) { errorMessage.value = readableError(error) }
  finally { busy.value = false }
}
onMounted(load)
</script>
<template>
  <section class="space-y-6">
    <div><h1 class="text-3xl font-bold">Usuarios</h1><p class="opacity-60">Solo administradores. Las contraseñas se gestionan en Firebase Auth.</p></div>
    <div v-if="errorMessage" class="alert alert-error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <form class="card border border-base-300 bg-base-100" @submit.prevent="createUser"><div class="card-body grid gap-4 md:grid-cols-2">
      <h2 class="card-title md:col-span-2">Nuevo usuario</h2>
      <label class="form-control"><span class="label-text">Nombre</span><input v-model="form.display_name" class="input input-bordered" required minlength="2" /></label>
      <label class="form-control"><span class="label-text">Correo</span><input v-model="form.email" type="email" class="input input-bordered" required /></label>
      <label class="form-control"><span class="label-text">Contraseña temporal (mín. 8)</span><input v-model="form.password" type="password" class="input input-bordered" minlength="8" required autocomplete="new-password" /></label>
      <label class="form-control"><span class="label-text">Rol</span><select v-model="form.role" class="select select-bordered"><option>VIEWER</option><option>COORDINATOR</option><option>ADMIN</option></select></label>
      <button class="btn btn-primary w-fit md:col-span-2" type="submit" :disabled="busy">Crear usuario</button>
    </div></form>
    <div class="overflow-x-auto rounded-box border border-base-300 bg-base-100"><table class="table table-zebra">
      <thead><tr><th>Correo</th><th>Nombre</th><th>Rol</th><th>Activo</th><th>Acción</th></tr></thead>
      <tbody><tr v-for="user in users" :key="user.uid"><td>{{ user.email }}</td><td>{{ user.display_name }}</td><td>{{ user.role }}</td><td>{{ user.active ? 'Sí' : 'No' }}</td><td><button class="btn btn-xs" @click="edit(user)">Editar</button></td></tr></tbody>
    </table></div>
    <form v-if="editingId" class="card border border-base-300 bg-base-100" @submit.prevent="save"><div class="card-body gap-3">
      <h2 class="card-title">Editar perfil</h2>
      <input v-model="draft.display_name" class="input input-bordered" required />
      <select v-model="draft.role" class="select select-bordered"><option>VIEWER</option><option>COORDINATOR</option><option>ADMIN</option></select>
      <label class="label cursor-pointer justify-start gap-3"><input v-model="draft.active" type="checkbox" class="checkbox" />Activo</label>
      <div class="flex gap-2"><button class="btn btn-primary" :disabled="busy">Guardar</button><button type="button" class="btn" @click="editingId = ''">Cancelar</button></div>
    </div></form>
  </section>
</template>
