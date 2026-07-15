<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import ProfileCompanyList from '~/components/profile/ProfileCompanyList.vue'
import { getCarriers, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'

definePageMeta({
  layout: 'profile',
  title: 'Перевозчики',
})

const page = ref(1)
const perPage = ref(10)
const {
  data: carriers,
  pending: loadingCarriers,
  refresh: refreshCarriers,
} = await getCarriers(page.value, perPage.value)

const handleRemove = async (company: PartnerCompany) => {
  await removeCompanyRelation(company.id, CompanyRelationType.CARRIER)
  await refreshCarriers()
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg p-4">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Перевозчики</h2>
      <ProfileCompanyList
        :companies="carriers || []"
        :loading="loadingCarriers"
        type="carrier"
        :show-contracts-link="false"
        :on-remove="handleRemove"
        @refresh="refreshCarriers"
      />
    </div>
  </div>
</template>
