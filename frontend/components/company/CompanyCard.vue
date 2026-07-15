<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import { getFullImageUrl } from '~/types/company'

const props = defineProps<{
  partner: PartnerCompany
  /** Показывать «Посмотреть договоры» (список Контрагенты) */
  showContractsLink?: boolean
}>()

const emit = defineEmits<{
  (e: 'remove', company: PartnerCompany): void
}>()

const router = useRouter()

const navigateToCompany = () => {
  router.push(`/companies/${props.partner.slug}`)
}

const openDocuments = () => {
  router.push({
    path: '/profile/documents',
    query: { counterparty_id: String(props.partner.id) },
  })
}

const handleDelete = () => {
  emit('remove', props.partner)
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-4 flex items-start space-x-4">
    <div class="flex-shrink-0">
      <NuxtImg
        :src="getFullImageUrl(partner.logo) || '/images/default-company-logo.png'"
        :alt="partner.fullName"
        class="w-16 h-16 rounded-lg object-cover"
      />
    </div>

    <div class="flex-grow">
      <div class="flex justify-between items-start gap-3 flex-wrap">
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
        <div class="flex flex-wrap gap-2 items-center">
          <MessageButtonBySlug
            :company-slug="partner.slug"
            :company-name="partner.fullName"
            variant="ghost"
            size="sm"
            custom-text="Написать сообщение"
          />
          <UButton
            v-if="showContractsLink !== false"
            label="Посмотреть договоры"
            color="neutral"
            variant="ghost"
            size="sm"
            @click="openDocuments"
          />
          <button
            type="button"
            class="text-red-600 hover:text-red-800 text-sm font-medium px-2"
            @click="handleDelete"
          >
            Удалить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
