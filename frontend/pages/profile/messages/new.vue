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
const { data: chat, pending, error } = await createChat({
  participantId: toCompanySlug,
  participantName: toCompanyName,
  participantLogo: toCompanyLogo
})

// Immediately redirect to the chat if it was created
if (chat.value) {
  router.push(`/profile/messages/${chat.value.id}`)
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