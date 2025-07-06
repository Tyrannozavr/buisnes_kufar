export interface RegisterStep1Data {
  firstName?: string
  lastName?: string
  patronymic?: string
  email: string
  phone: string
  recaptcha_token: string
  agreement?: boolean
}

export interface RegisterStep2Data {
  inn: string
  position: {
    label: string,
    value: string,
  }
  password: string
  confirmPassword: string
  token: string
}

export interface VerifyTokenResponse {
  is_valid: boolean,
  company_name: string,
  logo_url: string,
  company_slug?: string,
  company_id?: number
}

export interface RegisterStep1Response {
  statusCode: number
  message: string
}

export interface RegisterStep2Response {
  access_token: string
  user: {
    id: number
    email: string
    first_name: string | null
    last_name: string | null
    patronymic: string | null
    phone: string
    inn: string
    position: string
    is_active: boolean
    created_at: string
  }
}

export interface RegisterValidationResponse {
  is_valid: boolean
  message?: string
}

export interface ApiError {
  message: string
  detail?: string
  errors?: Record<string, string[]>
  statusCode: number
} 