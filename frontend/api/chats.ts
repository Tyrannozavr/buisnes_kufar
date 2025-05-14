import type { Chat, ChatMessage } from '~/types/chat'
import type { UseFetchOptions } from 'nuxt/app'

export const useChatsApi = () => {
  const getChats = (userId: string, options: UseFetchOptions<Chat[]> = {}) => {
    return useApi<Chat[]>('/chats', {
      query: { userId },
      ...options
    })
  }

  const getChatById = (chatId: string, options: UseFetchOptions<Chat> = {}) => {
    return useApi<Chat>(`/chats/${chatId}`, options)
  }

  const getChatMessages = (chatId: string, options: UseFetchOptions<ChatMessage[]> = {}) => {
    return useApi<ChatMessage[]>(`/chats/${chatId}/messages`, options)
  }

  const sendMessage = (chatId: string, data: { senderId: string, content: string }, options: UseFetchOptions<ChatMessage> = {}) => {
    return useApi<ChatMessage>(`/chats/${chatId}/send`, {
      method: 'POST',
      body: {
        chatId,
        ...data
      },
      ...options
    })
  }

  const createChat = (data: { participantId: string, participantName: string, participantLogo?: string }, options: UseFetchOptions<Chat> = {}) => {
    return useApi<Chat>('/chats/create', {
      method: 'POST',
      body: data,
      ...options
    })
  }

  return {
    getChats,
    getChatById,
    getChatMessages,
    sendMessage,
    createChat
  }
} 