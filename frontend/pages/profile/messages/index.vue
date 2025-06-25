<script setup lang="ts">
import type { Chat } from '~/types/chat'
import { useChatsApi } from '~/api/chats'
import { useUserStore } from '~/stores/user'

definePageMeta({
  layout: 'profile'
})

const router = useRouter()
const { getChats } = useChatsApi()
const userStore = useUserStore()

// Получаем ID текущей компании из store
const currentCompanyId = userStore.companyId

const { data: chats, pending, error } = await getChats()

const handleChatSelect = (chatId: number) => {
  router.push(`/profile/messages/${chatId}`)
}

// Функция для получения собеседника (не текущая компания)
const getOtherParticipant = (chat: any) => {
  return chat.participants.find((p: any) => p.company_id !== currentCompanyId)
}

// Функция для форматирования даты
const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Нет даты'
    }
    return date.toLocaleDateString('ru-RU')
  } catch {
    return 'Нет даты'
  }
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)] flex">
    <!-- Chat list sidebar -->
    <div class="w-1/3 border-r border-gray-200 overflow-y-auto">
      <div v-if="pending" class="flex items-center justify-center h-full">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>

      <div v-else-if="error" class="flex items-center justify-center h-full">
        <div class="text-center text-red-500">
          <UIcon name="i-heroicons-exclamation-circle" class="h-12 w-12 mx-auto mb-2" />
          <p>Произошла ошибка при загрузке чатов</p>
        </div>
      </div>

      <div v-else-if="!chats?.length" class="flex items-center justify-center h-full">
        <div class="text-center text-gray-500">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="h-12 w-12 mx-auto mb-2" />
          <p>У вас пока нет сообщений</p>
        </div>
      </div>

      <div v-else class="space-y-1">
        <div
          v-for="chat in chats"
          :key="chat.id"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          @click="handleChatSelect(chat.id)"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <LazyNuxtImg
                :src="getOtherParticipant(chat)?.company_logo_url || '/images/default-company-logo.png'"
                :alt="getOtherParticipant(chat)?.company_name"
                class="w-12 h-12 rounded-full object-cover"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-start">
                <h3 class="text-sm font-medium text-gray-900 truncate">
                  {{ getOtherParticipant(chat)?.company_name || 'Неизвестная компания' }}
                </h3>
                <span class="text-xs text-gray-500">
                  {{ formatDate(chat.updated_at) }}
                </span>
              </div>
              <p class="text-sm text-gray-500 truncate">
                {{ chat.last_message?.content || 'Нет сообщений' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Welcome message -->
    <div class="flex-1 flex items-center justify-center bg-gray-50">
      <div class="text-center text-gray-500 max-w-md px-4">
        <UIcon name="i-heroicons-chat-bubble-left-right" class="h-16 w-16 mx-auto mb-4" />
        <h2 class="text-xl font-semibold mb-2">Добро пожаловать в чат</h2>
        <p class="text-gray-600">
          Выберите чат из списка слева, чтобы начать общение или создать новый диалог
        </p>
      </div>
    </div>
  </div>
</template>