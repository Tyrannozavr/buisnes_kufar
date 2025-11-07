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

export interface AdminDeletionRejectRequest {
  reason?: string
}

// Список всех доступных прав в системе
export const AVAILABLE_PERMISSIONS = {
  company_management: "Управление компанией",
  company_data: "Данные компании", 
  products: "Продукция",
  announcements: "Объявления",
  business_connections: "Бизнес-связи",
  partners: "Партнеры",
  suppliers: "Поставщики", 
  buyers: "Покупатели",
  documents: "Документы",
  contracts: "Договоры",
  sales: "Продажи",
  purchases: "Закупки",
  communications: "Коммуникации",
  messages: "Сообщения",
  administration: "Администрирование"
} as const
