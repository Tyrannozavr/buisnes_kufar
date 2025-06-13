<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import { getFullImageUrl } from '~/types/company'
import { useChatsApi } from '~/api/chats'
import { useCompaniesApi } from '~/api/companies'

const props = defineProps<{
  partner: PartnerCompany
}>()

const router = useRouter()
const { createChat } = useChatsApi()
const { deletePartnerById } = useCompaniesApi()

const navigateToCompany = () => {
  router.push(`/company/${props.partner.slug}`)
}

const navigateToMessage = async () => {
  try {
    const { data: chat } = await createChat({
      participantId: props.partner.slug,
      participantName: props.partner.fullName,
      participantLogo: props.partner.logo || undefined
    })

    if (chat.value) {
      router.push(`/profile/messages/${chat.value.id}`)
    }
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось создать чат',
      color: 'error'
    })
  }
}

const handleDelete = async () => {
  try {
    await deletePartnerById(props.partner.slug)
    useToast().add({
      title: 'Успешно',
      description: 'Компания удалена из списка',
      color: 'success'
    })
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось удалить компанию',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-4 flex items-start space-x-4">
    <!-- Company Logo -->
    <div class="flex-shrink-0">
      <NuxtImg
        :src="getFullImageUrl(partner.logo) || '/images/default-company-logo.png'"
        :alt="partner.fullName"
        class="w-16 h-16 rounded-lg object-cover"
      />
    </div>

    <!-- Company Info -->
    <div class="flex-grow">
      <div class="flex justify-between items-start">
        <div>
          <h3
            class="text-lg font-semibold text-blue-600 cursor-pointer hover:text-blue-800"
            @click="navigateToCompany"
          >
            {{ partner.fullName }}
          </h3>
          <p class="text-gray-600 text-sm">
            {{ partner.country }}, {{ partner.region }}, {{ partner.city }}
          </p>
          <p class="text-gray-700 mt-1">{{ partner.businessType }}</p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="navigateToMessage"
            class="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Написать сообщение
          </button>
          <button
            @click="handleDelete"
            class="text-red-600 hover:text-red-800 text-sm font-medium"
          >
            Удалить из списка
          </button>
        </div>
      </div>
    </div>
  </div>
</template> 