<script setup lang="ts">
import type { Chat } from '~/types/chat'
import { useChatsApi } from '~/api/chats'

definePageMeta({
  layout: 'profile',
  title: 'Новое сообщение',
  hideLastBreadcrumb: true
})

const route = useRoute()
const router = useRouter()
const { createChat } = useChatsApi()

// Get company info from query params
const toCompanySlug = route.query.to as string
const toCompanyName = route.query.name as string
const toCompanyLogo = route.query.logo as string

// Create new chat and redirect
const pending = ref(true)
const error = ref<Error | null>(null)
let chat: Chat | null = null

try {
  chat = await createChat({
    participantSlug: toCompanySlug,
    participantName: toCompanyName,
    participantLogo: toCompanyLogo
  })
  pending.value = false
} catch (err) {
  error.value = err as Error
  pending.value = false
}

// Immediately redirect to the chat if it was created
if (chat) {
  router.push(`/profile/messages/${chat.id}`)
}

// Handle error
if (error.value) {
  useToast().add({
    title: 'Ошибка',
    description: 'Не удалось создать чат',
    color: 'error'
  })
  router.push('/profile/messages')
}
</script>

<template>
  <div class="h-[calc(100vh-16rem)] flex items-center justify-center">
    <div v-if="pending" class="text-center">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500 mx-auto mb-4" />
      <p class="text-gray-500">Создание чата...</p>
    </div>
  </div>
</template> 