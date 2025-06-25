export interface ChatParticipant {
  id: number
  company_id: number
  user_id: number
  company_name: string
  company_slug: string
  company_logo: string
  company_logo_url: string
  user_name: string
  is_admin: boolean
  joined_at: string
}

export interface Chat {
  id: number
  title?: string | null
  is_group: boolean
  participants: ChatParticipant[]
  last_message?: ChatMessage | null
  created_at: string
  updated_at: string
}

export interface ChatId {
  chat_id: number
}

export interface ChatFile {
  name: string
  url: string
  type: string
  size: number
}

export interface ChatMessage {
  id: number
  chat_id: number
  sender_company_id: number
  sender_user_id: number
  content: string
  file_path?: string
  file_name?: string
  file_size?: number
  file_type?: string
  is_read: boolean
  created_at: string
  updated_at: string
}

export interface CreateChatResponse {
  id: number
  title?: string | null
  participantLogo?: string
  participantName: string
} 