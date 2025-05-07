<script setup lang="ts">
import type { Chat } from '~/types/chat'

definePageMeta({
  layout: 'profile'
})
// Fetch chats
const { data: chats, pending: chatsPending } = await useFetch<Chat[]>('/api/chats', {
  query: {
    userId: 'company1' // TODO: Replace with actual company ID from auth
  }
})

const router = useRouter()

// Handle chat selection
const handleChatSelect = (chatId: string) => {
  router.push(`/profile/messages/${chatId}`)
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)]">
    <div v-if="chatsPending" class="flex items-center justify-center h-full">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
    </div>

    <div v-else-if="!chats?.length" class="flex items-center justify-center h-full">
      <div class="text-center text-gray-500">
        <UIcon name="i-heroicons-chat-bubble-left-right" class="h-12 w-12 mx-auto mb-2" />
        <p>У вас пока нет сообщений</p>
      </div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="chat in chats"
        :key="chat.id"
        class="bg-white rounded-lg shadow p-4 hover:bg-gray-50 cursor-pointer transition-colors"
        @click="handleChatSelect(chat.id)"
      >
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <img
              :src="chat.participants[0]?.logo || '/images/default-company-logo.png'"
              :alt="chat.participants[0]?.name"
              class="w-12 h-12 rounded-full object-cover"
            />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-start">
              <h3 class="text-sm font-medium text-gray-900 truncate">
                {{ chat.participants[0]?.name }}
              </h3>
              <span class="text-xs text-gray-500">
                {{ new Date(chat.updatedAt).toLocaleDateString('ru-RU') }}
              </span>
            </div>
            <p class="text-sm text-gray-500 truncate">
              {{ chat.lastMessage?.content || 'Нет сообщений' }}
            </p>
          </div>
          <div v-if="chat.unreadCount > 0" class="flex-shrink-0">
            <UBadge color="primary" size="sm">
              {{ chat.unreadCount }}
            </UBadge>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 