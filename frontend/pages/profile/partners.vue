<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"
import { getPartners, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'

definePageMeta({
  layout: 'profile'
})

const {
  data: partners,
  pending: loadingPartners,
  refresh: refreshPartners
} = await getPartners()

const handleRemovePartner = async (partner: PartnerCompany) => {
  await removeCompanyRelation(partner.id, CompanyRelationType.PARTNER)
  await refreshPartners()
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