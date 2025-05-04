import { defineStore } from 'pinia'

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
    login(companyName: string, companyLogo: string) {
      this.isAuthenticated = true
      this.companyName = companyName
      this.companyLogo = companyLogo
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
