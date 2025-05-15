<script setup lang="ts">
import type {Chat, ChatMessage, ChatParticipant} from '~/types/chat'
import {useChatsApi} from '~/api/chats'

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

const {getChats, getChatById, getChatMessages, sendMessage} = useChatsApi()

// Получаем список всех чатов для боковой панели
const {data: chats, pending: chatsPending} = await getChats(userId)

// Получаем информацию о текущем чате
const {data: chat, pending: chatPending} = await getChatById(chatId)

// Получаем сообщения текущего чата
const {data: messages, pending: messagesPending, refresh: refreshMessages} = await getChatMessages(chatId)

const newMessage = ref('')
const showActionsModal = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)

const otherParticipant = computed(() => {
  if (!chat.value) return null
  return chat.value.participants.find((p: ChatParticipant) => p.id !== userId)
})

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
  }
}

const handleSendMessage = async () => {
  if (!newMessage.value.trim() && !selectedFile.value) return

  try {
    const formData = new FormData()
    formData.append('content', newMessage.value)
    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    }

    await sendMessage(chatId, {
      senderId: userId,
      content: newMessage.value,
      file: selectedFile.value
    })
    
    newMessage.value = ''
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
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

const getFileIcon = (mimeType: string) => {
  if (mimeType.startsWith('image/')) return 'i-heroicons-photo'
  if (mimeType.startsWith('video/')) return 'i-heroicons-video-camera'
  if (mimeType.startsWith('audio/')) return 'i-heroicons-musical-note'
  if (mimeType.includes('pdf')) return 'i-heroicons-document-text'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'i-heroicons-document-text'
  if (mimeType.includes('excel') || mimeType.includes('sheet')) return 'i-heroicons-table-cells'
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return 'i-heroicons-presentation-chart-line'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'i-heroicons-archive-box'
  return 'i-heroicons-document'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)] flex">
    <!-- Chat list sidebar -->
    <div class="w-1/3 border-r border-gray-200 overflow-y-auto">
      <div v-if="chatsPending" class="flex items-center justify-center h-full">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500"/>
      </div>

      <div v-else-if="!chats?.length" class="flex items-center justify-center h-full">
        <div class="text-center text-gray-500">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="h-12 w-12 mx-auto mb-2"/>
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
      <!-- Chat header -->
      <div v-if="chat && otherParticipant" class="flex items-center justify-between border-b px-6 py-4 bg-white">
        <NuxtLink
            :to="`/company/${otherParticipant.slug || otherParticipant.id}`"
            class="text-lg font-semibold text-blue-600 hover:underline truncate"
        >
          {{ otherParticipant.name }}
        </NuxtLink>
        <UModal>
          <UButton
              variant="subtle"
              color="neutral"
              class="p-2 rounded-full hover:bg-gray-100 border-none hover:border cursor-pointer"
              @click="showActionsModal = true">
            <UIcon name="i-heroicons-ellipsis-horizontal" class="w-6 h-6 text-gray-500"/>
          </UButton>
          <template #content>
            <div class="p-8 text-center text-gray-500">
              <p>Здесь появятся действия с чатом (например, показать все вложения).</p>
            </div>
          </template>
          <template #footer>
            <UButton @click="showActionsModal = false">
              Закрыть
            </UButton>
          </template>
        </UModal>
      </div>

      <div v-if="chatPending || messagesPending" class="flex-1 flex items-center justify-center">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500"/>
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
              <div v-if="message.content" class="mb-2">
                {{ message.content }}
              </div>
              <div v-if="message.file" class="mt-2">
                <a 
                  :href="message.file.url" 
                  target="_blank"
                  class="flex items-center gap-2 p-2 rounded bg-white/10 hover:bg-white/20 transition-colors"
                  :class="message.sender.id === userId ? 'text-blue-100' : 'text-blue-600'"
                >
                  <UIcon 
                    :name="getFileIcon(message.file.type)" 
                    class="w-5 h-5 flex-shrink-0" 
                  />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">{{ message.file.name }}</p>
                    <p class="text-xs opacity-75">
                      {{ formatFileSize(message.file.size) }}
                    </p>
                  </div>
                  <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5 flex-shrink-0" />
                </a>
              </div>
              <p class="text-xs mt-2" :class="message.sender.id === userId ? 'text-blue-100' : 'text-gray-500'">
                {{ new Date(message.createdAt).toLocaleTimeString() }}
              </p>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-200 p-4">
          <form class="flex gap-4" @submit.prevent="handleSendMessage">
            <div class="flex-1 flex items-center gap-2">
              <button
                  type="button"
                  class="p-2 text-gray-500 hover:text-gray-700 focus:outline-none"
                  @click="fileInput?.click()"
              >
                <UIcon name="i-heroicons-paper-clip" class="w-6 h-6" />
              </button>
              <input
                  ref="fileInput"
                  type="file"
                  class="hidden"
                  @change="handleFileSelect"
              />
              <input
                  v-model="newMessage"
                  type="text"
                  placeholder="Введите сообщение..."
                  class="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            <button
                type="submit"
                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Отправить
            </button>
          </form>
          <div v-if="selectedFile" class="mt-2 flex items-center gap-2 text-sm text-gray-600">
            <UIcon name="i-heroicons-paper-clip" class="w-4 h-4" />
            {{ selectedFile.name }}
            <button
                type="button"
                class="text-red-500 hover:text-red-700"
                @click="selectedFile = null"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>
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

  <!-- Actions Modal -->
  <UModal v-model="showActionsModal">
    <div class="p-6">
      <h3 class="text-lg font-semibold mb-4">Файлы в чате</h3>
      <div v-if="messages?.some(m => m.file)" class="space-y-4">
        <div
            v-for="message in messages.filter(m => m.file)"
            :key="message.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <UIcon 
              :name="getFileIcon(message.file?.type || '')" 
              class="w-6 h-6 text-gray-500" 
            />
            <div>
              <p class="text-sm font-medium">{{ message.file?.name }}</p>
              <p class="text-xs text-gray-500">
                Отправлено {{ new Date(message.createdAt).toLocaleString('ru-RU') }}
              </p>
            </div>
          </div>
          <a
              :href="message.file?.url"
              target="_blank"
              class="text-blue-600 hover:text-blue-800"
          >
            <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5" />
          </a>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 py-4">
        <p>В этом чате пока нет прикрепленных файлов</p>
      </div>
    </div>
    <template #footer>
      <UButton @click="showActionsModal = false">
        Закрыть
      </UButton>
    </template>
  </UModal>
</template>