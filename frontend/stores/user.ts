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
      const authApi = useAuthApi()
      const tokenResponse = await authApi.verifyToken()
      this.isAuthenticated = true
      this.companyName = tokenResponse.company_name
      this.companyLogo = tokenResponse.logo_url
      this.companySlug = tokenResponse.company_slug || ''
      this.companyId = tokenResponse.company_id || 0
    },
    
    logout() {
      this.isAuthenticated = false
      this.companyName = ''
      this.companyLogo = ''
      this.companySlug = ''
      this.companyId = 0
      // Clear any other user data as needed
    }
  },
  
  persist: true,
})
