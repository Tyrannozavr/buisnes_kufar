<script setup lang="ts">
import type { Chat } from '~/types/chat'
import { formatMoscowDate } from '~/utils/datetime'
import { useChatsApi } from '~/api/chats'
import { useUserStore } from '~/stores/user'
import { onChatPresenceMessage } from '~/composables/useChatPresence'
import { useChatUnreadStore } from '~/stores/chatUnread'
import { companyAvatarUrl, onCompanyAvatarError } from '~/utils/companyAvatar'
import { chatLastMessagePreview } from '~/utils/chatPreview'
import { getActiveChatIdFromRoute } from '~/utils/chatUnread'

definePageMeta({
  layout: 'profile',
  title: 'Сообщения',
})

const route = useRoute()
const router = useRouter()
const { getChats } = useChatsApi()
const userStore = useUserStore()
const chatUnreadStore = useChatUnreadStore()

const currentCompanyId = userStore.companyId

const { data: chats, pending, error, refresh: refreshChats } = await getChats()

const syncUnreadBadges = () => {
  if (chats.value) chatUnreadStore.setFromChats(chats.value)
}

watch(chats, syncUnreadBadges, { deep: true, immediate: true })

onMounted(() => {
  void refreshChats().then(syncUnreadBadges)

  const unsubscribe = onChatPresenceMessage((message) => {
    if (message.type === 'new_message') {
      const payload = message.message as {
        sender_company_id?: number
        content?: string
        created_at?: string
        id?: number
        file_name?: string
        file_type?: string
      } | undefined
      const senderId = Number(payload?.sender_company_id)
      const targetChatId = Number(message.chat_id)
      const viewerId = Number(currentCompanyId)
      const activeChatId = getActiveChatIdFromRoute(route)
      const viewingThisChat =
        document.visibilityState === 'visible' &&
        activeChatId != null &&
        activeChatId === targetChatId

      if (
        targetChatId &&
        senderId &&
        viewerId &&
        senderId !== viewerId &&
        chats.value &&
        !viewingThisChat
      ) {
        const item = chats.value.find((c) => c.id === targetChatId)
        if (item) {
          item.unread_count = (item.unread_count ?? 0) + 1
          item.last_message = {
            id: payload?.id ?? 0,
            chat_id: targetChatId,
            sender_company_id: senderId,
            sender_user_id: 0,
            content: payload?.content ?? '',
            file_name: payload?.file_name,
            file_type: payload?.file_type,
            is_read: false,
            created_at: payload?.created_at ?? new Date().toISOString(),
            updated_at: payload?.created_at ?? new Date().toISOString(),
          }
          syncUnreadBadges()
        }
      }
    }

    if (message.type === 'new_message' || message.type === 'messages_read') {
      void refreshChats().then(syncUnreadBadges)
    }
  })
  onUnmounted(unsubscribe)
})

const handleChatSelect = (chatId: number) => {
  router.push(`/profile/messages/${chatId}`)
}

const getOtherParticipant = (chat: Chat) => {
  const myId = Number(currentCompanyId)
  return chat.participants.find((p) => Number(p.company_id) !== myId)
}

const formatDate = (dateString: string) => formatMoscowDate(dateString)

const hasChats = computed(() => (chats.value?.length ?? 0) > 0)
</script>

<template>
  <div class="bg-white shadow rounded-lg overflow-hidden h-[calc(100vh-16rem)] flex flex-col lg:flex-row">
    <!-- Список чатов -->
    <div class="w-full lg:w-1/3 border-r border-gray-200 overflow-y-auto flex flex-col min-h-0">
      <div class="p-4 border-b border-gray-200 sticky top-0 z-10 bg-white flex items-center justify-between gap-3">
        <h2 class="text-lg font-medium text-gray-900">Сообщения</h2>
        <UButton
          to="/profile/messages/new"
          color="primary"
          size="sm"
          icon="i-heroicons-plus"
          label="Написать"
          class="cursor-pointer"
        />
      </div>

      <div v-if="pending" class="flex flex-1 items-center justify-center p-4">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>

      <div v-else-if="error" class="p-4">
        <p class="text-sm text-red-600">Не удалось загрузить чаты</p>
      </div>

      <div v-else-if="!hasChats" class="p-4">
        <p class="text-sm text-gray-500">Нет чатов</p>
      </div>

      <div v-else class="space-y-0">
        <div
          v-for="chat in chats"
          :key="chat.id"
          class="p-4 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0"
          @click="handleChatSelect(chat.id)"
        >
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <img
                :src="companyAvatarUrl(getOtherParticipant(chat)?.company_logo_url)"
                :alt="getOtherParticipant(chat)?.company_name || 'Компания'"
                class="w-10 h-10 rounded-full object-cover border border-gray-200 bg-gray-100"
                @error="onCompanyAvatarError"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-start mb-1">
                <h3 class="text-sm font-medium text-gray-900 truncate">
                  {{ getOtherParticipant(chat)?.company_name || 'Неизвестная компания' }}
                </h3>
                <span class="text-xs text-gray-500 flex-shrink-0 ml-2">
                  {{ formatDate(chat.updated_at) }}
                </span>
              </div>
              <p class="text-sm text-gray-500 truncate leading-relaxed">
                {{ chatLastMessagePreview(chat.last_message) }}
              </p>
            </div>
            <div v-if="(chat.unread_count ?? 0) > 0" class="flex-shrink-0">
              <UBadge color="primary" size="sm">
                {{ (chat.unread_count ?? 0) > 99 ? '99+' : chat.unread_count }}
              </UBadge>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Правая панель: пусто без чатов; подсказка — если чаты есть -->
    <div class="hidden lg:flex flex-1 items-center justify-center bg-gray-50">
      <div v-if="hasChats" class="text-center text-gray-500 max-w-sm px-4">
        <h2 class="text-lg font-medium text-gray-900 mb-1">Выберите чат</h2>
        <p class="text-sm text-gray-500">
          Откройте диалог слева или нажмите «Написать»
        </p>
      </div>
    </div>
  </div>
</template>
