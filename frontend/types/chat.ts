export interface Chat {
  id: string
  participants: {
    id: string
    name: string
    logo?: string
  }[]
  lastMessage?: Message
  unreadCount: number
  updatedAt: string
}

export interface Message {
  id: string
  chatId: string
  senderId: string
  content: string
  createdAt: string
  isRead: boolean
}

export interface ChatMessage {
  id: string
  sender: {
    id: string
    name: string
    logo?: string
  }
  content: string
  createdAt: string
  isRead: boolean
} 