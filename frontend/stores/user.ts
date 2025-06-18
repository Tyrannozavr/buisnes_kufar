import {defineStore} from 'pinia'
import {AUTH_API, useAuthApi} from "~/api/auth";

interface UserState {
  isAuthenticated: boolean
  companyName: string
  companyLogo: string
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    isAuthenticated: false,
    companyName: '',
    companyLogo: '',
    // Add other user-related state as needed
  }),
  
  actions: {
    async login() {
      const authApi = useAuthApi()
      const tokenResponse = await authApi.verifyToken()
      this.isAuthenticated = true
      this.companyName = tokenResponse.company_name
      this.companyLogo = tokenResponse.logo_url
    },
    
    logout() {
      this.isAuthenticated = false
      this.companyName = ''
      this.companyLogo = ''
      // Clear any other user data as needed
    }
  },
  
  persist: true,
})
