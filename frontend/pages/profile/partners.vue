<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"



definePageMeta({
  layout: 'profile'
})

const {
  data: partners,
  pending: loadingPartners,
  refresh: refreshPartners
} = await useApi<PartnerCompany[]>('/company/partners')

const handleRemovePartner = async (partner: PartnerCompany) => {
  try {
    await useApi(`/company/partners/${partner.slug}`, {
      method: 'DELETE'
    })
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
  <ProfileLayout>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Партнеры</h2>
      <CompaniesList
        :companies="partners || []"
        :loading="loadingPartners"
        type="partner"
        @remove="handleRemovePartner"
      />
    </div>
  </ProfileLayout>
</template> 