import {defineStore} from 'pinia'
import {AUTH_API, useAuthApi} from "~/api/auth";

interface UserState {
  isAuthenticated: boolean
  companyName: string
  companyLogo: string
  companySlug: string
  companyId: number
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    isAuthenticated: false,
    companyName: '',
    companyLogo: '',
    companySlug: '',
    companyId: 0,
    // Add other user-related state as needed
  }),
  
  actions: {
    async login() {
      console.log('👤 UserStore.login() called')
      const authApi = useAuthApi()
      
      // Get token from cookie
      const accessToken = useCookie('access_token')
      console.log('🍪 Token in user store:', accessToken.value ? 'Present' : 'Missing')
      
      console.log('🔍 Calling authApi.verifyToken()...')
      const tokenResponse = await authApi.verifyToken(accessToken.value || undefined)
      console.log('✅ Token verification successful:', tokenResponse)
      
      this.isAuthenticated = true
      this.companyName = tokenResponse.company_name
      this.companyLogo = tokenResponse.logo_url
      this.companySlug = tokenResponse.company_slug || ''
      this.companyId = tokenResponse.company_id || 0
      
      console.log('👤 User state updated:', {
        isAuthenticated: this.isAuthenticated,
        companyName: this.companyName,
        companyId: this.companyId
      })
    },
    
    async logout() {
      console.log('🚪 UserStore.logout() called')
      
      // Call backend logout API
      try {
        const config = useRuntimeConfig()
        const apiBaseUrl = config.public.apiBaseUrl
        await $fetch(`${apiBaseUrl}/v1/auth/logout`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        console.log('✅ Backend logout successful')
      } catch (error) {
        console.error('❌ Backend logout error:', error)
        // Continue with local logout even if backend fails
      }
      
      // Clear cookie
      const accessToken = useCookie('access_token')
      accessToken.value = null
      
      // Clear cookie via document.cookie as well
      if (process.client) {
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax'
        
        // Clear localStorage
        localStorage.removeItem('cart')
        localStorage.removeItem('user')
        console.log('🗑️ localStorage cleared')
      }
      
      // Clear store state
      this.isAuthenticated = false
      this.companyName = ''
      this.companyLogo = ''
      this.companySlug = ''
      this.companyId = 0
      
      console.log('✅ Logout completed - cookie, localStorage and store cleared')
    }
  },
  
  persist: true,
})
