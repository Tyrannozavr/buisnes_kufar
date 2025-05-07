<script setup lang="ts">
import type { Chat, ChatMessage } from '~/types/chat'

const selectedChatId = ref<string | undefined>(undefined)

// Fetch chats
const { data: chats, pending: chatsPending } = await useFetch<Chat[]>('/api/chats', {
  query: {
    userId: 'company1' // TODO: Replace with actual company ID from auth
  }
})

// Get selected chat info
const selectedChat = computed(() => {
  if (!selectedChatId.value || !chats.value) return undefined
  return chats.value.find(chat => chat.id === selectedChatId.value)
})

// Fetch messages for selected chat
const { data: messages, pending: messagesPending, refresh: refreshMessages } = await useFetch<ChatMessage[]>(() => `/api/chats/${selectedChatId.value}/messages`, {
  query: {
    chatId: selectedChatId.value
  },
  watch: [selectedChatId]
})

// Handle chat selection
const handleChatSelect = (chatId: string) => {
  selectedChatId.value = chatId
}

// Handle sending a new message
const handleSendMessage = async (content: string) => {
  if (!selectedChatId.value) return

  try {
    await $fetch(`/api/chats/${selectedChatId.value}/send`, {
      method: 'POST',
      body: {
        chatId: selectedChatId.value,
        senderId: 'company1', // TODO: Replace with actual company ID from auth
        content
      }
    })

    // Refresh messages after sending
    await refreshMessages()
  } catch (error) {
    console.error('Failed to send message:', error)
    // Show error toast
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось отправить сообщение',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)] flex">
    <!-- Chat List -->
    <div class="w-1/3 border-r">
      <ChatList
        :chats="chats || []"
        :loading="chatsPending"
        :selected-chat-id="selectedChatId"
        @select="handleChatSelect"
      />
    </div>

    <!-- Chat Messages -->
    <div class="flex-1">
      <template v-if="selectedChatId">
        <ChatMessages
          :messages="messages || []"
          :loading="messagesPending"
          :chat-info="selectedChat"
          current-user-id="company1"
          @send="handleSendMessage"
        />
      </template>
      <div v-else class="h-full flex items-center justify-center text-gray-500">
        <div class="text-center">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="h-12 w-12 mx-auto mb-2" />
          <p>Выберите чат, чтобы начать общение</p>
        </div>
      </div>
    </div>
  </div>
</template> 