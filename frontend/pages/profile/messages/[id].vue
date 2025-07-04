<script setup lang="ts">
import type {ChatParticipant} from '~/types/chat'
import {useChatsApi} from '~/api/chats'
import { useWebSocket } from '~/composables/useWebSocket'

// Define page meta with hideLastBreadcrumb flag
definePageMeta({
  layout: 'profile',
  title: 'Сообщения',
  hideLastBreadcrumb: true
})

const route = useRoute()
const router = useRouter()
const chatId = parseInt(route.params.id as string)

// Получаем данные пользователя из store
const userStore = useUserStore()

const {getChats, getChatById, getChatMessages, sendMessage, getChatFiles} = useChatsApi()

// Получаем список всех чатов для боковой панели
const {data: chats, pending: chatsPending} = await getChats()

// Получаем информацию о текущем чате
const {data: chat, pending: chatPending} = await getChatById(chatId)

// Получаем сообщения текущего чата
const {data: messages, pending: messagesPending, refresh: refreshMessages} = await getChatMessages(chatId)

// Получаем файлы чата
const {data: files, pending: filesPending} = await getChatFiles(chatId)

const newMessage = ref('')
const showFilesModal = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isTyping = ref(false)
const typingTimeout = ref<NodeJS.Timeout | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)

// WebSocket setup
const config = useRuntimeConfig()
const accessToken = useCookie('access_token')
const wsUrl = `${config.public.apiBaseUrl?.replace('http', 'ws')}/v1/chats/${chatId}/ws?token=${accessToken.value}`

// Функция для прокрутки к последнему сообщению
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Функция для добавления нового сообщения
const addNewMessage = (message: any) => {
  if (messages.value) {
    // Проверяем, нет ли уже такого сообщения
    const existingIndex = messages.value.findIndex(m => m.id === message.id)
    if (existingIndex === -1) {
      messages.value.push(message)
      scrollToBottom()
    }
  }
}

const { 
  isConnected, 
  isConnecting, 
  error: wsError, 
  connect: connectWs, 
  disconnect: disconnectWs, 
  sendTyping 
} = useWebSocket(wsUrl, {
  onMessage: (message) => {
    console.log('WebSocket message received:', message)
    
    if (message.type === 'new_message') {
      // Добавляем новое сообщение в список только если это не наше временное сообщение
      if (!message.message.is_temp) {
        addNewMessage(message.message)
      }
    } else if (message.type === 'typing_indicator') {
      // Обрабатываем индикатор печати
      if (message.user_id !== userStore.companyId) {
        isTyping.value = message.is_typing
      }
    } else if (message.type === 'connection_established') {
      console.log('WebSocket connection established')
    }
  },
  onOpen: () => {
    console.log('WebSocket connected')
  },
  onClose: () => {
    console.log('WebSocket disconnected')
  },
  onError: (error) => {
    console.error('WebSocket error:', error)
  }
})

// Подключаемся к WebSocket при загрузке страницы
onMounted(() => {
  connectWs()
  // Прокручиваем к последнему сообщению при загрузке
  scrollToBottom()
})

// Отключаемся при уходе со страницы
onUnmounted(() => {
  disconnectWs()
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
})

// Следим за изменениями в сообщениях
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

const otherParticipant = computed(() => {
  if (!chat.value) return null
  return chat.value.participants.find((p: ChatParticipant) => p.company_id !== userStore.companyId)
})

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
  }
}

const handleTyping = () => {
  // Отправляем индикатор печати
  sendTyping(true)
  
  // Сбрасываем таймер
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
  
  // Останавливаем индикатор через 2 секунды
  typingTimeout.value = setTimeout(() => {
    sendTyping(false)
  }, 2000)
}

const handleSendMessage = async () => {
  if (!newMessage.value.trim() && !selectedFile.value) return

  try {
    // Останавливаем индикатор печати
    sendTyping(false)
    if (typingTimeout.value) {
      clearTimeout(typingTimeout.value)
    }

    // Создаем временное сообщение для немедленного отображения
    const tempMessage = {
      id: Date.now(), // Временный ID
      chat_id: chatId,
      sender_company_id: userStore.companyId,
      sender_user_id: userStore.companyId, // Предполагаем, что user_id = company_id
      content: newMessage.value,
      file_path: selectedFile.value ? selectedFile.value.name : null,
      file_name: selectedFile.value ? selectedFile.value.name : null,
      file_size: selectedFile.value ? selectedFile.value.size : null,
      file_type: selectedFile.value ? selectedFile.value.type : null,
      is_read: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_temp: true // Флаг для временного сообщения
    }

    // Добавляем временное сообщение сразу
    addNewMessage(tempMessage)

    // Очищаем поле ввода
    const messageContent = newMessage.value
    const fileToSend = selectedFile.value
    newMessage.value = ''
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }

    // Отправляем сообщение на сервер
    const messageResponse = await sendMessage(chatId, {
      senderId: userStore.companyId || 0,
      content: messageContent,
      file: fileToSend || undefined
    })

    // Заменяем временное сообщение на реальное
    if (messages.value && messageResponse.data.value) {
      const tempIndex = messages.value.findIndex(m => m.is_temp)
      if (tempIndex !== -1) {
        messages.value[tempIndex] = messageResponse.data.value
      }
    }

  } catch (error) {
    console.error('Failed to send message:', error)
    // Удаляем временное сообщение в случае ошибки
    if (messages.value) {
      const tempIndex = messages.value.findIndex(m => m.is_temp)
      if (tempIndex !== -1) {
        messages.value.splice(tempIndex, 1)
      }
    }
  }
}

const handleChatSelect = (newChatId: number) => {
  router.push(`/profile/messages/${newChatId}`)
}

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
  <div class="flex h-[calc(100vh-16rem)]">
    <!-- Боковая панель с чатами -->
    <div class="w-80 border-r border-gray-200 flex flex-col">
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold">Сообщения</h2>
      </div>
      
      <div v-if="chatsPending" class="flex-1 flex items-center justify-center">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-6 w-6 text-gray-500"/>
      </div>
      
      <div v-else class="flex-1 overflow-y-auto">
        <div
          v-for="chatItem in chats"
          :key="chatItem.id"
          class="p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
          :class="{ 'bg-blue-50 border-blue-200': chatItem.id === chatId }"
          @click="handleChatSelect(chatItem.id)"
        >
          <div class="flex items-center space-x-3">
            <img
              :src="chatItem.participants.find(p => p.company_id !== userStore.companyId)?.company_logo_url || '/images/default-company-logo.png'"
              :alt="chatItem.participants.find(p => p.company_id !== userStore.companyId)?.company_name"
              class="w-10 h-10 rounded-full object-cover"
            />
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm truncate">
                {{ chatItem.participants.find(p => p.company_id !== userStore.companyId)?.company_name }}
              </p>
              <p v-if="chatItem.last_message" class="text-xs text-gray-500 truncate">
                {{ chatItem.last_message.content }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Основная область чата -->
    <div class="flex-1 flex flex-col">
      <!-- Заголовок чата -->
      <div v-if="chat" class="p-4 border-b border-gray-200 bg-white">
        <NuxtLink
            :to="`/companies/${otherParticipant?.company_slug}`"
            class="flex items-center space-x-3"
        >
          <NuxtImg
            :src="otherParticipant?.company_logo_url || '/images/default-company-logo.png'"
            :alt="otherParticipant?.company_name"
            class="w-10 h-10 rounded-full object-cover"
          />
          <div class="flex-1">
            <h3 class="font-semibold">{{ otherParticipant?.company_name }}</h3>
            <div class="flex items-center space-x-2">
              <div class="flex items-center space-x-1">
                <div 
                  class="w-2 h-2 rounded-full"
                  :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
                ></div>
                <span class="text-xs text-gray-500">
                  {{ isConnected ? 'Онлайн' : 'Офлайн' }}
                </span>
              </div>
              <span v-if="isTyping" class="text-xs text-blue-500">
                печатает...
              </span>
            </div>
          </div>
        </NuxtLink>
      </div>

      <div v-if="chatPending || messagesPending" class="flex-1 flex items-center justify-center">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500"/>
      </div>

      <template v-else-if="chat">
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4 max-h-[calc(100vh-200px)]">
          <div
              v-for="message in messages"
              :key="message.id"
              class="flex"
              :class="{ 'justify-end': message.sender_company_id?.toString() === userStore.companyId?.toString() }"
          >
            <div
                class="max-w-[70%] p-4 rounded-lg"
                :class="message.sender_company_id?.toString() === userStore.companyId?.toString() ? 'bg-blue-500 text-white' : 'bg-gray-100'"
            >
              <div v-if="message.content" class="mb-2">
                {{ message.content }}
              </div>
              <div v-if="message.file_path" class="mt-2">
                <a
                    :href="message.file_path"
                    target="_blank"
                    class="flex items-center gap-2 p-2 rounded bg-white/10 hover:bg-white/20 transition-colors"
                    :class="message.sender_company_id?.toString() === userStore.companyId?.toString() ? 'text-blue-100' : 'text-blue-600'"
                >
                  <UIcon
                      :name="getFileIcon(message.file_type || '')"
                      class="w-5 h-5 flex-shrink-0"
                  />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">{{ message.file_name }}</p>
                    <p class="text-xs opacity-75">
                      {{ formatFileSize(message.file_size || 0) }}
                    </p>
                  </div>
                  <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5 flex-shrink-0"/>
                </a>
              </div>
              <p class="text-xs mt-2" :class="message.sender_company_id?.toString() === userStore.companyId?.toString() ? 'text-blue-100' : 'text-gray-500'">
                {{ new Date(message.created_at).toLocaleTimeString() }}
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
                <UIcon name="i-heroicons-paper-clip" class="w-6 h-6"/>
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
                  @input="handleTyping"
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
            <UIcon name="i-heroicons-paper-clip" class="w-4 h-4"/>
            {{ selectedFile.name }}
            <button
                type="button"
                class="text-red-500 hover:text-red-700"
                @click="selectedFile = null"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4"/>
            </button>
          </div>
        </div>
      </template>

      <div v-else class="flex-1 flex items-center justify-center">
        <p class="text-gray-500">Чат не найден</p>
      </div>
    </div>
  </div>
</template>