<script setup lang="ts">
import type { ChatMessage } from '~/types/chat'

const props = defineProps<{
  messages: ChatMessage[]
  loading?: boolean
  currentUserId: string
  chatInfo?: {
    id: string
    participants: {
      id: string
      name: string
      logo?: string
    }[]
  }
}>()

const emit = defineEmits<{
  (e: 'send', content: string): void
}>()

const newMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

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

const sendMessage = () => {
  if (newMessage.value.trim()) {
    emit('send', newMessage.value.trim())
    newMessage.value = ''
  }
}

// Get the other participant (not current user)
const otherParticipant = computed(() => {
  if (!props.chatInfo) return null
  return props.chatInfo.participants.find(p => p.id !== props.currentUserId)
})

// Scroll to bottom when messages change
watch(() => props.messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}, { deep: true })
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Chat Header -->
    <div v-if="otherParticipant" class="border-b p-4">
      <NuxtLink 
        :to="`/companies/${otherParticipant.slug}`"
        class="flex items-center space-x-3 hover:bg-gray-50 p-2 rounded-lg transition-colors"
      >
        <img
          :src="otherParticipant.logo || '/images/default-company-logo.png'"
          :alt="otherParticipant.name"
          class="w-10 h-10 rounded-full object-cover"
        />
        <div>
          <h3 class="font-medium text-gray-900">{{ otherParticipant.name }}</h3>
          <p class="text-sm text-gray-500">Перейти на страницу компании</p>
        </div>
      </NuxtLink>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
    </div>

    <template v-else>
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto p-4 space-y-4"
      >
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex"
          :class="{ 'justify-end': message.sender.id === currentUserId }"
        >
          <div
            class="max-w-[70%] rounded-lg px-4 py-2"
            :class="{
              'bg-primary-500 text-white': message.sender.id === currentUserId,
              'bg-gray-100 text-gray-900': message.sender.id !== currentUserId
            }"
          >
            <div class="flex items-center space-x-2 mb-1">
              <img
                v-if="message.sender.id !== currentUserId"
                :src="message.sender.logo || '/images/default-company-logo.png'"
                :alt="message.sender.name"
                class="w-6 h-6 rounded-full"
              />
              <span class="text-sm font-medium">
                {{ message.sender.name }}
              </span>
            </div>
            <p class="text-sm">{{ message.content }}</p>
            <span class="text-xs opacity-75 mt-1 block">
              {{ formatDate(message.createdAt) }}
            </span>
          </div>
        </div>
      </div>

      <div class="border-t p-4">
        <form @submit.prevent="sendMessage" class="flex space-x-2">
          <UInput
            v-model="newMessage"
            placeholder="Введите сообщение..."
            class="flex-1"
          />
          <UButton
            type="submit"
            color="primary"
            :disabled="!newMessage.trim()"
          >
            Отправить
          </UButton>
        </form>
      </div>
    </template>
  </div>
</template> 