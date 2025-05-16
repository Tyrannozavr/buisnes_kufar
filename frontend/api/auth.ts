interface ApiResponse {
  success: boolean
  message: string
}

interface EmailChangeParams {
  email: string
  code: string
}

interface PasswordChangeParams {
  oldPassword: string
  newPassword: string
}

interface PasswordResetParams {
  email: string
  code: string
  newPassword: string
}

export const AUTH_API = {
  RECOVER_PASSWORD: '/api/auth/recover-password',
  VERIFY_CODE: '/api/auth/verify-code',
  RESET_PASSWORD: '/api/auth/reset-password',
  CHANGE_EMAIL: '/api/auth/change-email',
  CHANGE_PASSWORD: '/api/auth/change-password'
} as const 

export const authApi = {
  // Восстановление пароля
  async sendRecoveryCode(email: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/api/auth/recover-password', {
      method: 'POST',
      body: { email }
    })
  },

  async verifyRecoveryCode(email: string, code: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/api/auth/verify-code', {
      method: 'POST',
      body: { email, code }
    })
  },

  async resetPassword(params: PasswordResetParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/api/auth/reset-password', {
      method: 'POST',
      body: params
    })
  },

  // Смена email
  async sendEmailChangeCode(email: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/api/auth/recover-password', {
      method: 'POST',
      body: { email }
    })
  },

  async changeEmail(params: EmailChangeParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/api/auth/change-email', {
      method: 'POST',
      body: params
    })
  },

  // Смена пароля
  async changePassword(params: PasswordChangeParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/api/auth/change-password', {
      method: 'POST',
      body: params
    })
  }
} 