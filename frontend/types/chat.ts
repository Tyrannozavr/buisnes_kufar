export interface ChatParticipant {
  id: string
  name: string
  logo?: string
  slug?: string
}

export interface Chat {
  id: string
  participants: ChatParticipant[]
  lastMessage?: ChatMessage
  createdAt: string
  updatedAt: string
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
  id: string
  chatId: string
  sender: ChatParticipant
  content: string
  file?: ChatFile
  createdAt: string
  updatedAt: string
} 