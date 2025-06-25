import type {
  ApiError,
  RegisterStep1Data,
  RegisterStep2Data,
  RegisterValidationResponse,
  VerifyTokenResponse
} from '~/types/auth'

import type {ApiResponse, EmailChangeParams, PasswordChangeParams, PasswordResetParams} from '~/types/api'

import {useCookie} from 'nuxt/app'
import { AUTH_URLS } from '~/constants/urls'

export const AUTH_API = {
  REGISTER_STEP1: '/v1/auth/register/step1',
  REGISTER_STEP2: '/v1/auth/register/step2',
  VERIFY_TOKEN: '/v1/auth/verify-token',
  VERIFY_REGISTRATION_TOKEN: '/v1/auth/registration/verify-token',
  RECOVER_PASSWORD: '/v1/auth/recover-password',
  VERIFY_CODE: '/v1/auth/verify-code',
  RESET_PASSWORD: '/v1/auth/reset-password',
  CHANGE_EMAIL: '/v1/auth/change-email',
  CHANGE_PASSWORD: '/v1/auth/change-password',
  LOGIN: '/v1/auth/login',
  COMPANY_ME: '/v1/company/me',
  LOGOUT: '/v1/auth/logout'
} as const 
export const authApi = {
  // Восстановление пароля
  async sendRecoveryCode(email: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/v1/auth/recover-password', {
      method: 'POST',
      body: { email }
    })
  },

  async verifyRecoveryCode(email: string, code: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/v1/auth/verify-code', {
      method: 'POST',
      body: { email, code }
    })
  },

  async resetPassword(params: PasswordResetParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/v1/auth/reset-password', {
      method: 'POST',
      body: params
    })
  },

  // Смена email
  async sendEmailChangeCode(email: string): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/v1/auth/recover-password', {
      method: 'POST',
      body: { email }
    })
  },

  async changeEmail(params: EmailChangeParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/v1/auth/change-email', {
      method: 'POST',
      body: params
    })
  },

  // Смена пароля
  async changePassword(params: PasswordChangeParams): Promise<ApiResponse> {
    return await $fetch<ApiResponse>('/v1/auth/change-password', {
      method: 'POST',
      body: params
    })
  },

  async logout(): Promise<void> {
    try {
      console.log('🚪 Calling backend logout API...')
      await $fetch(`${apiBaseUrl}${AUTH_API.LOGOUT}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      console.log('✅ Backend logout successful')
    } catch (error: any) {
      console.error('❌ Backend logout error:', error)
      // Don't throw error, continue with local logout
    }
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
  const accessToken = useCookie('access_token')
  const { $api } = useNuxtApp()

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
      const response = await $fetch<RegisterValidationResponse>(`${apiBaseUrl}${AUTH_API.VERIFY_REGISTRATION_TOKEN}/${token}`, {
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

  const verifyToken = async (token?: string): Promise<VerifyTokenResponse> => {
    console.log('🔍 verifyToken called')
    
    // Use provided token or get from cookie
    const tokenToUse = token || useCookie('access_token').value
    console.log('🍪 Token to use in verifyToken:', tokenToUse ? 'Present' : 'Missing')
    if (tokenToUse) {
      console.log('🔍 Token preview in verifyToken:', tokenToUse.substring(0, 20) + '...')
    }
    
    try {
      // Make direct fetch with token in headers
      const config = useRuntimeConfig()
      const apiBaseUrl = config.public.apiBaseUrl
      
      const response = await $fetch<VerifyTokenResponse>(`${apiBaseUrl}${AUTH_API.VERIFY_TOKEN}`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokenToUse}`
        },
        credentials: 'include'
      })
      
      console.log('✅ verifyToken successful:', response)
      return response
    } catch (error) {
      console.error('❌ verifyToken failed:', error)
      throw error
    }
  }

  const registerStep2 = async (data: RegisterStep2Data): Promise<{ message: string }> => {
    try {
      const response = await $fetch<{ access_token: string, token_type: string }>(`${apiBaseUrl}${AUTH_API.REGISTER_STEP2}`, {
        method: 'POST',
        body: {
          token: data.token,
          inn: data.inn,
          position: data.position.value,
          password: data.password
        },
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })

      // Set the token in a cookie
      accessToken.value = response.access_token

      return { message: 'Registration completed successfully' }
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const login = async (inn: string, password: string): Promise<void> => {
    console.log('🔐 login function called with INN:', inn)
    try {
      const response = await $fetch<{ access_token: string, token_type: string }>(`${apiBaseUrl}${AUTH_API.LOGIN}`, {
        method: 'POST',
        body: { inn, password },
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })

      console.log('✅ Login API response received:', {
        hasToken: !!response.access_token,
        tokenType: response.token_type,
        tokenPreview: response.access_token ? response.access_token.substring(0, 20) + '...' : 'No token'
      })

      // Set the token in a cookie (client-side only, with options)
      if (process.client) {
        console.log('🌐 Setting token in cookie (client-side)')
        // Установить через useCookie (Nuxt), но также явно через document.cookie для надёжности
        const cookie = useCookie('access_token', { path: '/', sameSite: 'lax' })
        cookie.value = response.access_token
        document.cookie = `access_token=${response.access_token}; path=/; SameSite=Lax`;
        console.log("🍪 Setting access token to cookie (client)", cookie.value ? 'Success' : 'Failed')
        console.log("🔍 Cookie value after setting:", cookie.value ? cookie.value.substring(0, 20) + '...' : 'No value')
        
        // Verify cookie was set
        const verifyCookie = useCookie('access_token')
        console.log("🔍 Verification - cookie value:", verifyCookie.value ? 'Present' : 'Missing')
      } else {
        console.log('🖥️ Server-side login, not setting cookie')
      }
    } catch (error: any) {
      console.error('❌ Login API error:', error)
      throw formatErrorResponse(error)
    }
  }

  const getCompanyInfo = async () => {
    try {
      const headers = new Headers({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      })
      
      if (accessToken.value) {
        headers.set('Authorization', `Bearer ${accessToken.value}`)
      }

      const response = await $fetch(`${apiBaseUrl}${AUTH_API.COMPANY_ME}`, {
        credentials: 'include',
        headers
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  // Смена пароля
  const changePassword = async (params: PasswordChangeParams): Promise<ApiResponse> => {
    return await $api.post(AUTH_URLS.CHANGE_PASSWORD, params)
  }

  // Смена email - запрос
  const requestEmailChange = async (newEmail: string, password: string): Promise<ApiResponse> => {
    return await $api.post(AUTH_URLS.REQUEST_EMAIL_CHANGE, {
      new_email: newEmail,
      password: password
    })
  }

  // Смена email - подтверждение
  const confirmEmailChange = async (token: string): Promise<ApiResponse> => {
    return await $api.post(AUTH_URLS.CONFIRM_EMAIL_CHANGE, {
      token: token
    })
  }

  // Сброс пароля - запрос
  const requestPasswordReset = async (email: string): Promise<ApiResponse> => {
    return await $api.post(AUTH_URLS.REQUEST_PASSWORD_RESET, {
      email: email
    })
  }

  // Сброс пароля - подтверждение
  const confirmPasswordReset = async (token: string, newPassword: string): Promise<ApiResponse> => {
    return await $fetch<ApiResponse>('/v1/auth/reset-password', {
      method: 'POST',
      body: { token, new_password: newPassword }
    })
  }

  const logout = async (): Promise<void> => {
    try {
      console.log('🚪 Calling backend logout API...')
      await $fetch(`${apiBaseUrl}${AUTH_API.LOGOUT}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      console.log('✅ Backend logout successful')
    } catch (error: any) {
      console.error('❌ Backend logout error:', error)
      // Don't throw error, continue with local logout
    }
  }

  return {
    registerStep1,
    validateRegistrationToken,
    verifyToken,
    registerStep2,
    login,
    getCompanyInfo,
    changePassword,
    requestEmailChange,
    confirmEmailChange,
    requestPasswordReset,
    confirmPasswordReset,
    logout
  }
} 