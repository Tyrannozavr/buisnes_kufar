<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"
import { usePartnersApi } from '~/api'

definePageMeta({
  layout: 'profile'
})

const { getPartners, removePartner } = usePartnersApi()

const {
  data: partners,
  pending: loadingPartners,
  refresh: refreshPartners
} = await getPartners()

const handleRemovePartner = async (partner: PartnerCompany) => {
  try {
    await removePartner(partner.slug)
    await refreshPartners()
    useToast().add({
      title: 'Успешно',
      description: 'Партнер удален из списка',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось удалить партнера',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Партнеры</h2>
      <CompaniesList
        :companies="partners || []"
        :loading="loadingPartners"
        type="partner"
        @remove="handleRemovePartner"
      />
    </div>
  </div>
</template>