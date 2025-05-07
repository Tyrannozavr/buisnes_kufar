<script setup lang="ts">
import type { Chat, ChatMessage } from '~/types/chat'

const route = useRoute()
const router = useRouter()
const chatId = route.params.id as string

// Fetch chat info
const { data: chat, pending: chatPending } = await useFetch<Chat>(`/api/chats/${chatId}`)

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

// Handle back button
const handleBack = () => {
  router.push('/profile/messages')
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)] flex flex-col">
    <!-- Back button -->
    <div class="mb-4">
      <UButton
        color="gray"
        variant="ghost"
        icon="i-heroicons-arrow-left"
        @click="handleBack"
      >
        Назад к списку чатов
      </UButton>
    </div>

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
            @click="handleBack"
          >
            Вернуться к списку чатов
          </UButton>
        </template>
      </UAlert>
    </div>
  </div>
</template> 