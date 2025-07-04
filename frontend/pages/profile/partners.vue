<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import ProfileCompanyList from '~/components/profile/ProfileCompanyList.vue'
import { getPartners, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'
import { ref } from 'vue'

definePageMeta({
  layout: 'profile'
})

const page = ref(1)
const perPage = ref(10)
const {
  data: partners,
  pending: loadingPartners,
  refresh: refreshPartners
} = await getPartners(page.value, perPage.value)

const handleRemovePartner = async (partner: PartnerCompany) => {
  await removeCompanyRelation(partner.id, CompanyRelationType.PARTNER)
  await refreshPartners()
}

const handleRefresh = async () => {
  await refreshPartners()
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Партнеры</h2>
      <ProfileCompanyList
        :companies="partners || []"
        :loading="loadingPartners"
        type="partner"
        :onRemove="handleRemovePartner"
        @refresh="handleRefresh"
      />
    </div>
  </div>
</template>