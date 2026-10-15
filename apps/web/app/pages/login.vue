<script setup lang="ts">
definePageMeta({ layout: 'auth' })
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const { login } = useAuth()
async function submit() {
  loading.value = true
  errorMessage.value = ''
  try { await login(email.value, password.value); await navigateTo('/dashboard') }
  catch (error) { errorMessage.value = readableError(error) }
  finally { loading.value = false }
}
</script>
<template>
  <form class="card border border-base-300 bg-base-100 shadow-xl" @submit.prevent="submit">
    <div class="card-body gap-4">
      <h1 class="text-3xl font-bold">AulaPlan</h1>
      <p class="text-sm opacity-60">Gestión académica y horarios inteligentes. IA opcional pendiente.</p>
      <div v-if="errorMessage" class="alert alert-error text-sm">{{ errorMessage }}</div>
      <label class="form-control"><span class="label-text mb-1">Correo</span><input v-model="email" type="email" class="input input-bordered" required autocomplete="username" /></label>
      <label class="form-control"><span class="label-text mb-1">Contraseña</span><input v-model="password" type="password" class="input input-bordered" required autocomplete="current-password" /></label>
      <button class="btn btn-primary" :disabled="loading">{{ loading ? 'Entrando…' : 'Iniciar sesión' }}</button>
    </div>
  </form>
</template>
