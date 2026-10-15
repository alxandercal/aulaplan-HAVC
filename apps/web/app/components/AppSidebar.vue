<script setup lang="ts">
const auth = useAuthStore()
const items = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Periodos', path: '/academic-periods' },
  { label: 'Profesores', path: '/teachers' },
  { label: 'Materias', path: '/subjects' },
  { label: 'Grupos', path: '/groups' },
  { label: 'Salones', path: '/rooms' },
  { label: 'Bloques', path: '/time-blocks' },
  { label: 'Ofertas académicas', path: '/offerings' },
  { label: 'Disponibilidad', path: '/availability' },
  { label: 'Restricciones', path: '/constraints' },
  { label: 'Generador', path: '/generator' },
  { label: 'Horarios', path: '/schedules' },
  { label: 'Usuarios', path: '/users', adminOnly: true },
]
</script>
<template>
  <aside class="min-h-full w-72 border-r border-base-300 bg-base-100 p-4">
    <NuxtLink to="/dashboard" class="mb-6 block text-xl font-bold">AulaPlan</NuxtLink>
    <ul class="menu gap-1 p-0">
      <li v-for="item in items.filter(entry => !entry.adminOnly || auth.role === 'ADMIN')" :key="item.path">
        <NuxtLink :to="item.path" active-class="menu-active">{{ item.label }}</NuxtLink>
      </li>
    </ul>
    <p class="mt-5 text-xs opacity-60">Motor determinista activo · IA pendiente</p>
  </aside>
</template>
