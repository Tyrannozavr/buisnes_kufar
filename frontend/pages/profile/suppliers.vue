<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"
import { getSuppliers, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'

definePageMeta({
  layout: 'profile'
})

const {
  data: suppliers,
  pending: loadingSuppliers,
  refresh: refreshSuppliers
} = await getSuppliers()

const handleRemoveSupplier = async (supplier: PartnerCompany) => {
  await removeCompanyRelation(supplier.id, CompanyRelationType.SUPPLIER)
  await refreshSuppliers()
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Поставщики</h2>
      <CompaniesList
        :companies="suppliers || []"
        :loading="loadingSuppliers"
        type="supplier"
        @remove="handleRemoveSupplier"
      />
    </div>
  </div>
</template> 