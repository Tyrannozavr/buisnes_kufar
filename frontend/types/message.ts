export interface Message {
  id: string
  fromCompanyId: string
  toCompanyId: string
  subject: string
  content: string
  createdAt: string
  isRead: boolean
} 