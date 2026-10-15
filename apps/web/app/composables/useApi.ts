import type { ApiErrorInfo } from '~/types'

export function readableError(error: unknown): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as { data?: ApiErrorInfo }).data
    if (data?.message) {
      if (Array.isArray(data.details)) {
        return `${data.message}: ${data.details.map(item => `${item.field}: ${item.message}`).join('; ')}`
      }
      return data.message
    }
  }
  return error instanceof Error ? error.message : 'Error inesperado al consultar el servidor.'
}

export function useApi() {
  const config = useRuntimeConfig()
  const { $firebaseAuth } = useNuxtApp()

  async function request<T>(path: string, options: Record<string, unknown> = {}): Promise<T> {
    const user = $firebaseAuth.currentUser
    const token = user ? await user.getIdToken() : null
    const headers = new Headers((options.headers as HeadersInit | undefined) || {})
    if (token) headers.set('Authorization', `Bearer ${token}`)
    // $fetch serializa el body JSON para POST/PUT automaticamente.
    return await $fetch<T>(path, {
      baseURL: config.public.apiBase,
      ...options,
      headers,
    })
  }

  return { request }
}
