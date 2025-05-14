export interface ChatParticipant {
  id: string
  name: string
  logo?: string
}

export interface Chat {
  id: string
  participants: ChatParticipant[]
  lastMessage?: ChatMessage
  createdAt: string
  updatedAt: string
}

export interface ChatMessage {
  id: string
  chatId: string
  sender: ChatParticipant
  content: string
  createdAt: string
  updatedAt: string
} 