import { signInWithEmailAndPassword, signOut } from 'firebase/auth'
import type { UserProfile } from '~/types'

export function useAuth() {
  const { $firebaseAuth } = useNuxtApp()
  const store = useAuthStore()
  const { request } = useApi()

  async function loadProfile() {
    const user = $firebaseAuth.currentUser
    if (!user) { store.setProfile(null); return }
    const profile = await request<UserProfile>('/auth/me')
    store.setProfile(profile)
  }

  async function login(email: string, password: string) {
    const credential = await signInWithEmailAndPassword($firebaseAuth, email, password)
    store.setFirebaseUser(credential.user)
    try {
      await loadProfile()
    } catch (error) {
      await signOut($firebaseAuth)
      store.setFirebaseUser(null)
      throw error
    }
  }

  async function logout() {
    await signOut($firebaseAuth)
    store.setFirebaseUser(null)
    store.setProfile(null)
    await navigateTo('/login')
  }
  return { login, logout, loadProfile }
}
