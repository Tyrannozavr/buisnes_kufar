<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"
import { getBuyers, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'

definePageMeta({
  layout: 'profile'
})

const {
  data: buyers,
  pending: loadingBuyers,
  refresh: refreshBuyers
} = await getBuyers()

const handleRemoveBuyer = async (buyer: PartnerCompany) => {
  console.log("Handle remove byers")
  await removeCompanyRelation(buyer.id, CompanyRelationType.BUYER)
  await refreshBuyers()
  // try {
  //   await deletePartnerById(props.partner.slug)
  //   useToast().add({
  //     title: 'Успешно',
  //     description: 'Компания удалена из списка',
  //     color: 'success'
  //   })
  // } catch (error) {
  //   useToast().add({
  //     title: 'Ошибка',
  //     description: 'Не удалось удалить компанию',
  //     color: 'error'
  //   })
  // }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Покупатели</h2>
      <CompaniesList
        :companies="buyers || []"
        :loading="loadingBuyers"
        type="buyer"
        @remove="handleRemoveBuyer"
      />
    </div>
  </div>
</template> 