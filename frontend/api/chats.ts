import type {Chat, ChatId, ChatMessage} from '~/types/chat'
import {type UseFetchOptions, useNuxtApp} from 'nuxt/app'
import type {CompanyResponse} from "~/types/company";

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

  const getChatFiles = (chatId: string, options: UseFetchOptions<any[]> = {}) => {
    return useApi<any[]>(`/chats/${chatId}/files`, options)
  }

  const sendMessage = (chatId: string, data: { senderId: string, content: string, file?: File }, options: UseFetchOptions<ChatMessage> = {}) => {
    const formData = new FormData()
    formData.append('chatId', chatId)
    formData.append('senderId', data.senderId)
    formData.append('content', data.content)
    if (data.file) {
      formData.append('file', data.file)
    }

    return useApi<ChatMessage>(`/chats/${chatId}/send`, {
      method: 'POST',
      body: formData,
      ...options
    })
  }

  const createChat = async (participantId: number): Promise<ChatId> => {
    const { $api } = useNuxtApp()
    try {
      return await $api.post('/v1/chats', { participant_id: participantId})
    } catch (error: any) {
      console.error('Error creating chat:', error)
      throw error
    }
  }

  return {
    getChats,
    getChatById,
    getChatMessages,
    getChatFiles,
    sendMessage,
    createChat
  }
} 