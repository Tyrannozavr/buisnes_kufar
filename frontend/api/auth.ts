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
  REGISTER_STEP1: '/v1/auth/register/step1',
  REGISTER_STEP2: '/v1/auth/register/step2',
  VERIFY_TOKEN: '/v1/auth/verify-token',
  RECOVER_PASSWORD: '/auth/recover-password',
  VERIFY_CODE: '/auth/verify-code',
  RESET_PASSWORD: '/auth/reset-password',
  CHANGE_EMAIL: '/auth/change-email',
  CHANGE_PASSWORD: '/auth/change-password',
  LOGIN: '/v1/auth/login',
  COMPANY_ME: '/v1/company/me'
} as const 

export const authApi = {
  // Восстановление пароля
  async sendRecoveryCode(email: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/auth/recover-password', {
      method: 'POST',
      body: { email }
    })
  },

  async verifyRecoveryCode(email: string, code: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/auth/verify-code', {
      method: 'POST',
      body: { email, code }
    })
  },

  async resetPassword(params: PasswordResetParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/auth/reset-password', {
      method: 'POST',
      body: params
    })
  },

  // Смена email
  async sendEmailChangeCode(email: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/auth/recover-password', {
      method: 'POST',
      body: { email }
    })
  },

  async changeEmail(params: EmailChangeParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/auth/change-email', {
      method: 'POST',
      body: params
    })
  },

  // Смена пароля
  async changePassword(params: PasswordChangeParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/auth/change-password', {
      method: 'POST',
      body: params
    })
  }
}

function formatErrorResponse(error: any): ApiError {
  // Handle $fetch error response
  if (error.response?._data) {
    return {
      message: error.response._data.message || error.response._data.detail || 'Произошла ошибка',
      detail: error.response._data.detail,
      errors: error.response._data.errors,
      statusCode: error.response.status
    }
  }
  // Handle direct error response
  if (error.response?.data) {
    return {
      message: error.response.data.message || error.response.data.detail || 'Произошла ошибка',
      detail: error.response.data.detail,
      errors: error.response.data.errors,
      statusCode: error.response.status
    }
  }
  // Handle other errors
  return {
    message: error.message || 'Произошла ошибка',
    detail: error.detail,
    statusCode: error.statusCode || 500
  }
}

export function useAuthApi() {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl

  const registerStep1 = async (data: RegisterStep1Data): Promise<void> => {
    try {
      await $fetch(`${apiBaseUrl}${AUTH_API.REGISTER_STEP1}`, {
        method: 'POST',
        body: {
          email: data.email,
          phone: data.phone,
          first_name: data.firstName,
          last_name: data.lastName,
          patronymic: data.patronymic
        },
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
    } catch (error: any) {
      console.log('Registration error:', error)
      throw formatErrorResponse(error)
    }
  }

  const validateRegistrationToken = async (token: string): Promise<RegisterValidationResponse> => {
    try {
      console.log('Validating token in API:', token)
      const response = await $fetch<RegisterValidationResponse>(`${apiBaseUrl}${AUTH_API.VERIFY_TOKEN}/${token}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      console.log('Token validation API response:', response)
      return response
    } catch (error: any) {
      console.log('Token validation API error:', error)
      throw formatErrorResponse(error)
    }
  }

  const registerStep2 = async (data: RegisterStep2Data): Promise<RegisterStep2Response> => {
    try {
      const response = await $fetch<RegisterStep2Response>(`${apiBaseUrl}${AUTH_API.REGISTER_STEP2}`, {
        method: 'POST',
        body: {
          token: data.token,
          inn: data.inn,
          position: data.position,
          password: data.password
        },
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const login = async (inn: string, password: string): Promise<void> => {
    try {
      await $fetch(`${apiBaseUrl}${AUTH_API.LOGIN}`, {
        method: 'POST',
        body: { inn, password },
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const getCompanyInfo = async () => {
    try {
      const response = await $fetch(`${apiBaseUrl}${AUTH_API.COMPANY_ME}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  return {
    registerStep1,
    validateRegistrationToken,
    registerStep2,
    login,
    getCompanyInfo
  }
} 