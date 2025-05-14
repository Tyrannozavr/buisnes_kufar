<script setup lang="ts">
import type { Chat, ChatMessage, ChatParticipant } from '~/types/chat'
import { useChatsApi } from '~/api/chats'

// Define page meta with hideLastBreadcrumb flag
definePageMeta({
  layout: 'profile',
  title: 'Сообщения',
  hideLastBreadcrumb: true
})

const route = useRoute()
const router = useRouter()
const chatId = route.params.id as string

// TODO: Заменить на реальный ID пользователя
const userId = 'company1'

const { getChats, getChatById, getChatMessages, sendMessage } = useChatsApi()

// Получаем список всех чатов для боковой панели
const { data: chats, pending: chatsPending } = await getChats(userId)

// Получаем информацию о текущем чате
const { data: chat, pending: chatPending } = await getChatById(chatId)

// Получаем сообщения текущего чата
const { data: messages, pending: messagesPending, refresh: refreshMessages } = await getChatMessages(chatId)

const newMessage = ref('')

const handleSendMessage = async () => {
  if (!newMessage.value.trim()) return

  try {
    await sendMessage(chatId, {
      senderId: userId,
      content: newMessage.value
    })
    newMessage.value = ''
    await refreshMessages()
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const handleChatSelect = (newChatId: string) => {
  router.push(`/profile/messages/${newChatId}`)
}

// Обновляем сообщения каждые 5 секунд
const refreshInterval = setInterval(() => {
  refreshMessages()
}, 5000)

onUnmounted(() => {
  clearInterval(refreshInterval)
})
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
                :src="chatItem.participants.find(p => p.id !== userId)?.logo || '/images/default-company-logo.png'"
                :alt="chatItem.participants.find(p => p.id !== userId)?.name"
                class="w-12 h-12 rounded-full object-cover"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-start">
                <h3 class="text-sm font-medium text-gray-900 truncate">
                  {{ chatItem.participants.find(p => p.id !== userId)?.name }}
                </h3>
                <span class="text-xs text-gray-500">
                  {{ new Date(chatItem.updatedAt).toLocaleDateString('ru-RU') }}
                </span>
              </div>
              <p class="text-sm text-gray-500 truncate">
                {{ chatItem.lastMessage?.content || 'Нет сообщений' }}
              </p>
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
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <div
            v-for="message in messages"
            :key="message.id"
            class="flex"
            :class="{ 'justify-end': message.sender.id === userId }"
          >
            <div
              class="max-w-[70%] p-4 rounded-lg"
              :class="message.sender.id === userId ? 'bg-blue-500 text-white' : 'bg-gray-100'"
            >
              <p>{{ message.content }}</p>
              <p class="text-xs mt-1" :class="message.sender.id === userId ? 'text-blue-100' : 'text-gray-500'">
                {{ new Date(message.createdAt).toLocaleTimeString() }}
              </p>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-200 p-4">
          <form @submit.prevent="handleSendMessage" class="flex gap-4">
            <input
              v-model="newMessage"
              type="text"
              placeholder="Введите сообщение..."
              class="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Отправить
            </button>
          </form>
        </div>
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