import type {Chat, ChatId, ChatMessage, CreateChatResponse} from '~/types/chat'
import {type UseFetchOptions, useNuxtApp} from 'nuxt/app'
import type {CompanyResponse} from "~/types/company";

export const useChatsApi = () => {
  const getChats = (options: UseFetchOptions<Chat[]> = {}) => {
    return useApi<Chat[]>('/v1/chats', options)
  }

  const getChatById = (chatId: string, options: UseFetchOptions<Chat> = {}) => {
    return useApi<Chat>(`/v1/chats/${chatId}`, options)
  }

  const getChatMessages = (chatId: string, options: UseFetchOptions<ChatMessage[]> = {}) => {
    return useApi<ChatMessage[]>(`/v1/chats/${chatId}/messages`, options)
  }

  const getChatFiles = (chatId: string, options: UseFetchOptions<any[]> = {}) => {
    return useApi<any[]>(`/v1/chats/${chatId}/files`, options)
  }

  const sendMessage = (chatId: string, data: { senderId: string, content: string, file?: File }, options: UseFetchOptions<ChatMessage> = {}) => {
    const formData = new FormData()
    formData.append('content', data.content)
    if (data.file) {
      formData.append('file', data.file)
    }

    return useApi<ChatMessage>(`/v1/chats/${chatId}/send`, {
      method: 'POST',
      body: formData,
      ...options
    })
  }

  const createChat = async (params: { 
    participantId?: number; 
    participantSlug?: string;
    participantName?: string;
    participantLogo?: string;
  }): Promise<CreateChatResponse> => {
    const { $api } = useNuxtApp()
    
    if (!params.participantId && !params.participantSlug) {
      throw new Error('Either participantId or participantSlug must be provided')
    }

    try {
      let response
      if (params.participantSlug) {
        // Создаем чат по slug
        response = await $api.post(`/v1/chats/by-slug/${params.participantSlug}`)
      } else {
        // Создаем чат по ID
        const payload = { participant_company_id: params.participantId }
        response = await $api.post('/v1/chats', payload)
      }
      
      // Возвращаем только необходимые данные для перехода к чату
      return {
        id: response.id.toString(),
        title: response.title || null,
        participantLogo: response.participants?.find((p: any) => p.company_id !== response.current_company_id)?.company_logo_url,
        participantName: response.participants?.find((p: any) => p.company_id !== response.current_company_id)?.company_name
      }
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