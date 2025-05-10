<script setup lang="ts">
import type { Chat, ChatMessage } from '~/types/chat'

// Define page meta with hideLastBreadcrumb flag
definePageMeta({
  layout: 'profile',
  title: 'Сообщения',
  hideLastBreadcrumb: true
})

const route = useRoute()
const router = useRouter()
const chatId = route.params.id as string

// Fetch chat info
const { data: chat, pending: chatPending } = await useFetch<Chat>(`/api/chats/${chatId}`)

// Set document title for browser tab
useHead(() => ({
  title: chat.value?.participants?.[1]?.name || 'Сообщения'
}))

// Fetch chats for the sidebar
const { data: chats, pending: chatsPending } = await useFetch<Chat[]>('/api/chats', {
  query: {
    userId: 'company1' // TODO: Replace with actual company ID from auth
  }
})

// Fetch messages
const { data: messages, pending: messagesPending, refresh: refreshMessages } = await useFetch<ChatMessage[]>(`/api/chats/${chatId}/messages`)

// Handle sending a new message
const handleSendMessage = async (content: string) => {
  try {
    await $fetch(`/api/chats/${chatId}/send`, {
      method: 'POST',
      body: {
        chatId,
        senderId: 'company1', // TODO: Replace with actual company ID from auth
        content
      }
    })

    // Refresh messages after sending
    await refreshMessages()
  } catch (error) {
    console.error('Failed to send message:', error)
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось отправить сообщение',
      color: 'error'
    })
  }
}

// Handle chat selection
const handleChatSelect = (newChatId: string) => {
  router.push(`/profile/messages/${newChatId}`)
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)] flex">
    <!-- Chat list sidebar -->
    <div class="w-1/3 border-r border-gray-200 overflow-y-auto">
      <div v-if="chatsPending" class="flex items-center justify-center h-full">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>

      <div v-else-if="!chats?.length" class="flex items-center justify-center h-full">
        <div class="text-center text-gray-500">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="h-12 w-12 mx-auto mb-2" />
          <p>У вас пока нет сообщений</p>
        </div>
      </div>

      <div v-else class="space-y-1">
        <div
          v-for="chatItem in chats"
          :key="chatItem.id"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          :class="{ 'bg-gray-50': chatItem.id === chatId }"
          @click="handleChatSelect(chatItem.id)"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <LazyNuxtImg
                :src="chatItem.participants[0]?.logo || '/images/default-company-logo.png'"
                :alt="chatItem.participants[0]?.name"
                class="w-12 h-12 rounded-full object-cover"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-start">
                <h3 class="text-sm font-medium text-gray-900 truncate">
                  {{ chatItem.participants[0]?.name }}
                </h3>
                <span class="text-xs text-gray-500">
                  {{ new Date(chatItem.updatedAt).toLocaleDateString('ru-RU') }}
                </span>
              </div>
              <p class="text-sm text-gray-500 truncate">
                {{ chatItem.lastMessage?.content || 'Нет сообщений' }}
              </p>
            </div>
            <div v-if="chatItem.unreadCount > 0" class="flex-shrink-0">
              <UBadge color="primary" size="sm">
                {{ chatItem.unreadCount }}
              </UBadge>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages area -->
    <div class="flex-1 flex flex-col">
      <div v-if="chatPending || messagesPending" class="flex-1 flex items-center justify-center">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>

      <template v-else-if="chat">
        <ChatMessages
          :messages="messages || []"
          :chat-info="chat"
          current-user-id="company1"
          @send="handleSendMessage"
        />
      </template>

      <div v-else class="flex-1 flex items-center justify-center">
        <UAlert
          color="error"
          title="Чат не найден"
          description="Запрашиваемый чат не существует или был удален"
          icon="i-heroicons-exclamation-circle"
        >
          <template #footer>
            <UButton
              color="error"
              variant="ghost"
              @click="router.push('/profile/messages')"
            >
              Вернуться к списку чатов
            </UButton>
          </template>
        </UAlert>
      </div>
    </div>
  </div>
</template>