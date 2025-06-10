export interface RegisterStep1Data {
  firstName?: string
  lastName?: string
  patronymic?: string
  email: string
  phone: string
  captcha: string
  agreement: boolean
}

export interface RegisterStep2Data {
  inn: string
  position: string
  password: string
  confirmPassword: string
}

export interface RegisterStep1Response {
  token: string
  statusCode: number
}

export interface RegisterStep2Response {
  companyName: string
  companyLogo: string
}

export interface RegisterValidationResponse {
  isValid: boolean
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
  statusCode: number
} 