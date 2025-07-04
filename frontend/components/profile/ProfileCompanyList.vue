<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from '~/components/company/CompaniesList.vue'
import { useToast } from 'vue-toastification'
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
    toast.success('Компания удалена из списка')
    emit('refresh')
  } catch (error) {
    toast.error('Не удалось удалить компанию')
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