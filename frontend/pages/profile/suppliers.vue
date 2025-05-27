<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"
import { useSuppliersApi } from '~/api'

definePageMeta({
  layout: 'profile'
})

const { getSuppliers, removeSupplier } = useSuppliersApi()

const {
  data: suppliers,
  pending: loadingSuppliers,
  refresh: refreshSuppliers
} = await getSuppliers()

const handleRemoveSupplier = async (supplier: PartnerCompany) => {
  try {
    await removeSupplier(supplier.slug)
    await refreshSuppliers()
    useToast().add({
      title: 'Успешно',
      description: 'Поставщик удален из списка',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось удалить поставщика',
      color: 'error'
    })
  }
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