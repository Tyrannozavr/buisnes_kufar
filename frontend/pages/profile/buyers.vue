<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"
import { useBuyersApi } from '~/api'


definePageMeta({
  layout: 'profile'
})

const { getBuyers, removeBuyer } = useBuyersApi()

const {
  data: buyers,
  pending: loadingBuyers,
  refresh: refreshBuyers
} = await getBuyers()

const handleRemoveBuyer = async (buyer: PartnerCompany) => {
  try {
    await removeBuyer(buyer.slug)
    await refreshBuyers()
    useToast().add({
      title: 'Успешно',
      description: 'Покупатель удален из списка',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось удалить покупателя',
      color: 'error'
    })
  }
}
</script>

<template>
  <ProfileLayout>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Покупатели</h2>
      <CompaniesList
        :companies="buyers || []"
        :loading="loadingBuyers"
        type="buyer"
        @remove="handleRemoveBuyer"
      />
    </div>
  </ProfileLayout>
</template> 