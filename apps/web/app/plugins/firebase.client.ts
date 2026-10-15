import { getApps, initializeApp } from 'firebase/app'
import { connectAuthEmulator, getAuth, onAuthStateChanged } from 'firebase/auth'
import type { UserProfile } from '~/types'

export default defineNuxtPlugin(async () => {
  const config = useRuntimeConfig()
  if (!config.public.firebaseProjectId || !config.public.firebaseApiKey) {
    throw new Error('Firebase sin configurar: revisa apps/web/.env')
  }
  const app = getApps()[0] || initializeApp({
    apiKey: config.public.firebaseApiKey,
    authDomain: config.public.firebaseAuthDomain,
    projectId: config.public.firebaseProjectId,
    storageBucket: config.public.firebaseStorageBucket,
    messagingSenderId: config.public.firebaseMessagingSenderId,
    appId: config.public.firebaseAppId,
  })
  const auth = getAuth(app)
  if (config.public.useFirebaseEmulators) {
    try {
      connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true })
    } catch {
      // Solo se intenta una vez en hot reload.
    }
  }
  const store = useAuthStore()
  await new Promise<void>((resolve) => {
    let first = true
    onAuthStateChanged(auth, async (user) => {
      store.setFirebaseUser(user)
      store.setProfile(null)
      if (user) {
        try {
          const token = await user.getIdToken()
          const profile = await $fetch<UserProfile>('/auth/me', {
            baseURL: config.public.apiBase,
            headers: { Authorization: `Bearer ${token}` },
          })
          store.setProfile(profile)
        } catch {
          // Sin perfil en Firestore: el backend denegara operaciones privadas.
        }
      }
      store.setReady(true)
      if (first) { first = false; resolve() }
    })
  })
  return { provide: { firebaseAuth: auth } }
})
