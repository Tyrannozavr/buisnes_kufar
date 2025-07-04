<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import ProfileCompanyList from '~/components/profile/ProfileCompanyList.vue'
import { getSuppliers, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'
import { ref } from 'vue'

definePageMeta({
  layout: 'profile'
})

const page = ref(1)
const perPage = ref(10)
const {
  data: suppliers,
  pending: loadingSuppliers,
  refresh: refreshSuppliers
} = await getSuppliers(page.value, perPage.value)

const handleRemoveSupplier = async (supplier: PartnerCompany) => {
  await removeCompanyRelation(supplier.id, CompanyRelationType.SUPPLIER)
  await refreshSuppliers()
}

const handleRefresh = async () => {
  await refreshSuppliers()
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Поставщики</h2>
      <ProfileCompanyList
        :companies="suppliers || []"
        :loading="loadingSuppliers"
        type="supplier"
        :onRemove="handleRemoveSupplier"
        @refresh="handleRefresh"
      />
    </div>
  </div>
</template> 