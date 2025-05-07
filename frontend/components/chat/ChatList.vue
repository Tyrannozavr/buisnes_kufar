<script setup lang="ts">
import type { Chat } from '~/types/chat'

const props = defineProps<{
  chats: Chat[]
  loading?: boolean
  selectedChatId?: string
}>()

const emit = defineEmits<{
  (e: 'select', chatId: string): void
}>()

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-4 border-b">
      <h2 class="text-xl font-semibold">Сообщения</h2>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
    </div>

    <div v-else-if="chats.length === 0" class="flex-1 flex items-center justify-center">
      <div class="text-center text-gray-500">
        <UIcon name="i-heroicons-chat-bubble-left-right" class="h-12 w-12 mx-auto mb-2" />
        <p>У вас пока нет сообщений</p>
      </div>
    </div>

    <div v-else class="flex-1 overflow-y-auto">
      <div
        v-for="chat in chats"
        :key="chat.id"
        class="p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors"
        :class="{ 'bg-gray-50': chat.id === selectedChatId }"
        @click="emit('select', chat.id)"
      >
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <NuxtImg
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
                {{ formatDate(chat.updatedAt) }}
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