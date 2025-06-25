export interface ApiResponse {
  success: boolean
  message: string
}

export interface EmailChangeParams {
  email: string
  code: string
}

export interface PasswordChangeParams {
  current_password: string
  new_password: string
}

export interface PasswordResetParams {
  email: string
  newPassword: string
  code: string
}

export interface PaginationResponse<T> {
  data: T[]
  pagination: {
    total: number
    page: number
    perPage: number
    totalPages: number
  }
} 