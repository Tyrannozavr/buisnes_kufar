<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import CompaniesList from "~/components/company/CompaniesList.vue"




definePageMeta({
  layout: 'profile'
})

const {
  data: suppliers,
  pending: loadingSuppliers,
  refresh: refreshSuppliers
} = await useApi<PartnerCompany[]>('/company/suppliers')

const handleRemoveSupplier = async (supplier: PartnerCompany) => {
  try {
    await useApi(`/company/suppliers/${supplier.slug}`, {
      method: 'DELETE'
    })
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
  <ProfileLayout>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Поставщики</h2>
      <CompaniesList
        :companies="suppliers || []"
        :loading="loadingSuppliers"
        type="supplier"
        @remove="handleRemoveSupplier"
      />
    </div>
  </ProfileLayout>
</template> 