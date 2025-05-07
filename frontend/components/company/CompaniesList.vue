<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompanyCard from './CompanyCard.vue'

type CompanyType = 'partner' | 'supplier' | 'buyer'

defineProps<{
  companies: PartnerCompany[]
  loading?: boolean
  type: CompanyType
}>()

const emit = defineEmits<{
  (e: 'remove', company: PartnerCompany): void
}>()

const handleRemove = (company: PartnerCompany) => {
  emit('remove', company)
}

const emptyMessages = {
  partner: 'У вас пока нет партнеров',
  supplier: 'У вас пока нет поставщиков',
  buyer: 'У вас пока нет покупателей'
}
</script>

<template>
  <div class="space-y-4">
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <template v-else>
      <div v-if="companies.length === 0" class="text-center py-8 text-gray-500">
        {{ emptyMessages[type] }}
      </div>

      <div v-else class="space-y-4">
        <CompanyCard
          v-for="company in companies"
          :key="company.slug"
          :partner="company"
          @remove="handleRemove"
        />
      </div>
    </template>
  </div>
</template> 