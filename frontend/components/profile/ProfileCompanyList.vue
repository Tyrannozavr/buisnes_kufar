<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from '~/components/company/CompaniesList.vue'
import { ref, watch } from 'vue'

const props = defineProps<{
  companies: PartnerCompany[]
  loading: boolean
  type: 'partner' | 'supplier' | 'buyer'
  onRemove: (company: PartnerCompany) => Promise<void>
}>()

const emit = defineEmits(['refresh'])
const toast = useToast()
const localCompanies = ref<PartnerCompany[]>(props.companies)

watch(() => props.companies, (val) => {
  localCompanies.value = val
})

const handleRemove = async (company: PartnerCompany) => {
  try {
    await props.onRemove(company)
    toast.add({ title: 'Компания удалена из списка', color: 'success' })
    emit('refresh')
  } catch (error) {
    toast.add({ title: 'Не удалось удалить компанию', color: 'error' })
  }
}
</script>

<template>
  <CompaniesList
    :companies="localCompanies"
    :loading="loading"
    :type="type"
    @remove="handleRemove"
  />
</template> 