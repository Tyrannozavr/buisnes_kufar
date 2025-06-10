import type {
  RegisterStep1Data,
  RegisterStep1Response,
  RegisterStep2Data,
  RegisterStep2Response,
  RegisterValidationResponse,
  ApiError
} from '~/types/auth'

import type {
  ApiResponse,
  EmailChangeParams,
  PasswordChangeParams,
  PasswordResetParams
} from '~/types/api'

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

export const useAuthApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase

  const registerStep1 = async (data: RegisterStep1Data): Promise<RegisterStep1Response> => {
    try {
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Simulate successful registration
      return {
        token: Math.random().toString(36).substring(2, 15),
        statusCode: 201
      }
    } catch (error: any) {
      if (error.response?.data) {
        throw {
          message: error.response.data.message || 'Произошла ошибка при регистрации',
          errors: error.response.data.errors,
          statusCode: error.response.status
        } as ApiError
      }
      throw {
        message: 'Произошла ошибка при регистрации',
        statusCode: 500
      } as ApiError
    }
  }

  const validateRegistrationToken = async (token: string): Promise<RegisterValidationResponse> => {
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    return {
      isValid: true
    }
  }

  const registerStep2 = async (token: string, data: RegisterStep2Data): Promise<RegisterStep2Response> => {
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    return {
      companyName: 'КосмоПорт',
      companyLogo: 'https://sun9-64.userapi.com/impg/IRHOxDleaLUBKmbafJ-j_3Z5Y-pYSMHou64S9A/kASuUQJDYrY.jpg?size=728x546&quality=96&sign=cdbf008a6c9d088a665d8e0b2fb5141a&c_uniq_tag=YJ1-dsBQHtkD4Ssy2wd5CaQpmFxJcQVaq3xbhyqOo38&type=album'
    }
  }

  return {
    registerStep1,
    validateRegistrationToken,
    registerStep2
  }
} 