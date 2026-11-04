<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import { useChatsApi } from '~/api/chats'
import { getCounterparties } from '~/api/company'
import { navigateToChatById, navigateToChatBySlug } from '~/composables/chat'
import { companyAvatarUrl, onCompanyAvatarError } from '~/utils/companyAvatar'

definePageMeta({
  layout: 'profile',
  title: 'Новое сообщение',
  hideLastBreadcrumb: true,
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { createChat } = useChatsApi()

const toCompanySlug = (route.query.to as string) || ''
const creating = ref(!!toCompanySlug)
const creatingId = ref<number | null>(null)

const {
  data: counterparties,
  pending: loadingCounterparties,
} = await getCounterparties(1, 50)

/** Прямой переход с карточки компании: ?to=slug */
if (toCompanySlug) {
  try {
    const chat = await createChat({
      participantSlug: toCompanySlug,
      participantName: (route.query.name as string) || undefined,
      participantLogo: (route.query.logo as string) || undefined,
    })
    if (chat?.id) {
      await router.replace(`/profile/messages/${chat.id}`)
    } else {
      throw new Error('Чат не создан')
    }
  } catch (e: any) {
    toast.add({
      title: 'Ошибка',
      description: e?.data?.detail || e?.message || 'Не удалось создать чат',
      color: 'error',
    })
    await router.replace('/profile/messages')
  } finally {
    creating.value = false
  }
}

const openChat = async (company: PartnerCompany) => {
  if (creatingId.value) return
  creatingId.value = company.id
  try {
    if (company.slug) {
      await navigateToChatBySlug(company.slug)
    } else {
      await navigateToChatById(company.id)
    }
  } catch (e: any) {
    toast.add({
      title: 'Ошибка',
      description: e?.data?.detail || e?.message || 'Не удалось создать чат',
      color: 'error',
    })
  } finally {
    creatingId.value = null
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg p-4 space-y-4">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg font-medium text-gray-900">Новое сообщение</h2>
        <UButton
          to="/profile/messages"
          color="neutral"
          variant="outline"
          size="sm"
          label="Назад"
          class="cursor-pointer"
        />
      </div>

      <div v-if="creating" class="flex items-center justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>

      <template v-else>
        <p class="text-sm text-gray-500">
          Выберите компанию из контрагентов, чтобы начать диалог.
        </p>

        <div v-if="loadingCounterparties" class="flex justify-center py-8">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
        </div>

        <p v-else-if="!counterparties?.length" class="text-sm text-gray-500">
          Контрагентов пока нет. Добавьте их в разделе «Контрагенты» или напишите со страницы компании.
        </p>

        <ul v-else class="divide-y divide-gray-100 border border-gray-200 rounded-lg">
          <li
            v-for="company in counterparties"
            :key="company.id"
          >
            <button
              type="button"
              class="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 cursor-pointer disabled:opacity-60"
              :disabled="creatingId === company.id"
              @click="openChat(company)"
            >
              <img
                :src="companyAvatarUrl(company.logo)"
                :alt="company.fullName"
                class="w-10 h-10 rounded-full object-cover border border-gray-200 bg-gray-100 shrink-0"
                @error="onCompanyAvatarError"
              />
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ company.fullName }}
                </p>
                <p v-if="company.city" class="text-xs text-gray-500 truncate">
                  {{ company.city }}
                </p>
              </div>
              <UIcon
                v-if="creatingId === company.id"
                name="i-heroicons-arrow-path"
                class="animate-spin h-5 w-5 text-gray-400 shrink-0"
              />
              <UIcon
                v-else
                name="i-heroicons-chevron-right"
                class="h-5 w-5 text-gray-400 shrink-0"
              />
            </button>
          </li>
        </ul>
      </template>
    </div>
  </div>
</template>
