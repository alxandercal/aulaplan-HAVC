export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return
  const store = useAuthStore()
  if (!store.ready) return
  if (!store.isAuthenticated && to.path !== '/login') return navigateTo('/login')
  if (store.isAuthenticated && to.path === '/login') return navigateTo('/dashboard')
  if (store.isAuthenticated && !store.profile && to.path !== '/login') {
    // La sesion existe en Firebase, pero falta perfil o API; mostrar error dentro del panel.
    return
  }
  if (to.path === '/users' && store.profile?.role !== 'ADMIN') return navigateTo('/dashboard')
})
