import type { ApiError } from '~/types/auth'

export interface EmployeeResponse {
  id: number
  user_id?: number
  company_id: number
  email: string
  first_name?: string
  last_name?: string
  patronymic?: string
  phone?: string
  position?: string
  role: 'owner' | 'admin' | 'user'
  status: 'pending' | 'active' | 'inactive' | 'deleted'
  permissions: Record<string, boolean>
  deletion_requested_at?: string
  deletion_requested_by?: number
  deletion_rejected_at?: string
  created_at: string
  updated_at?: string
  created_by?: number
}

export interface EmployeeCreate {
  email: string
  first_name?: string
  last_name?: string
  patronymic?: string
  phone?: string
  position?: string
  role: 'owner' | 'admin' | 'user'
  permissions?: Record<string, boolean>
}

export interface EmployeeUpdate {
  first_name?: string
  last_name?: string
  patronymic?: string
  phone?: string
  position?: string
  role?: 'owner' | 'admin' | 'user'
  permissions?: Record<string, boolean>
}

export interface EmployeeListResponse {
  employees: EmployeeResponse[]
  total: number
  page: number
  per_page: number
}

export interface PermissionUpdateRequest {
  permissions: Record<string, boolean>
}

export interface AdminDeletionRequest {
  reason?: string
}

export const EMPLOYEE_API = {
  EMPLOYEES: '/v1/auth/employees',
  COMPANY_EMPLOYEES: '/v1/auth/company-employees',
  PERMISSIONS: '/v1/auth/permissions',
  PROCESS_DELETIONS: '/v1/auth/process-pending-deletions',
  POSITIONS: '/v1/auth/positions',
  ROLES: '/v1/auth/roles'
} as const

function formatErrorResponse(error: any): ApiError {
  return {
    message: error.data?.detail || error.message || 'Произошла ошибка',
    errors: error.data?.errors || {},
    statusCode: error.statusCode || 500
  }
}

export function useEmployeeApi() {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  const accessToken = useCookie('access_token')

  const getEmployees = async (page: number = 1, per_page: number = 50): Promise<EmployeeListResponse> => {
    try {
      const response = await $fetch<EmployeeListResponse>(`${apiBaseUrl}${EMPLOYEE_API.COMPANY_EMPLOYEES}?page=${page}&per_page=${per_page}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const getEmployee = async (employeeId: number): Promise<EmployeeResponse> => {
    try {
      const response = await $fetch<EmployeeResponse>(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}/${employeeId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const createEmployee = async (employeeData: EmployeeCreate): Promise<EmployeeResponse> => {
    try {
      const response = await $fetch<EmployeeResponse>(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}`, {
        method: 'POST',
        body: employeeData,
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const updateEmployee = async (employeeId: number, employeeData: EmployeeUpdate): Promise<EmployeeResponse> => {
    try {
      const response = await $fetch<EmployeeResponse>(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}/${employeeId}`, {
        method: 'PUT',
        body: employeeData,
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const updateEmployeePermissions = async (employeeId: number, permissionsData: PermissionUpdateRequest): Promise<void> => {
    try {
      await $fetch(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}/${employeeId}/permissions`, {
        method: 'PUT',
        body: permissionsData,
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const deleteEmployee = async (employeeId: number): Promise<void> => {
    try {
      await $fetch(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}/${employeeId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const requestAdminDeletion = async (employeeId: number, deletionData: AdminDeletionRequest): Promise<void> => {
    try {
      await $fetch(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}/${employeeId}/request-deletion`, {
        method: 'POST',
        body: deletionData,
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const rejectAdminDeletion = async (employeeId: number): Promise<void> => {
    try {
      await $fetch(`${apiBaseUrl}${EMPLOYEE_API.EMPLOYEES}/${employeeId}/reject-deletion`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const getAvailablePermissions = async (): Promise<{ permissions: Record<string, string> }> => {
    try {
      const response = await $fetch<{ permissions: Record<string, string> }>(`${apiBaseUrl}${EMPLOYEE_API.PERMISSIONS}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const processPendingDeletions = async (): Promise<{ processed_count: number; message: string }> => {
    try {
      const response = await $fetch<{ processed_count: number; message: string }>(`${apiBaseUrl}${EMPLOYEE_API.PROCESS_DELETIONS}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const getPositions = async (): Promise<{ positions: Array<{value: string, label: string}> }> => {
    try {
      const response = await $fetch<{ positions: Array<{value: string, label: string}> }>(`${apiBaseUrl}${EMPLOYEE_API.POSITIONS}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  const getRoles = async (): Promise<{ roles: Array<{value: string, label: string, description: string}> }> => {
    try {
      const response = await $fetch<{ roles: Array<{value: string, label: string, description: string}> }>(`${apiBaseUrl}${EMPLOYEE_API.ROLES}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      return response
    } catch (error: any) {
      throw formatErrorResponse(error)
    }
  }

  return {
    getEmployees,
    getEmployee,
    createEmployee,
    updateEmployee,
    updateEmployeePermissions,
    deleteEmployee,
    requestAdminDeletion,
    rejectAdminDeletion,
    getAvailablePermissions,
    processPendingDeletions,
    getPositions,
    getRoles
  }
}
