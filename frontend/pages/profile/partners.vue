<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import ProfileCompanyList from '~/components/profile/ProfileCompanyList.vue'
import { getCounterparties, removeCounterparty } from '~/api/company'
import { ref } from 'vue'

definePageMeta({
  layout: 'profile',
  title: 'Контрагенты',
})

const page = ref(1)
const perPage = ref(10)
const {
  data: counterparties,
  pending: loadingCounterparties,
  refresh: refreshCounterparties,
} = await getCounterparties(page.value, perPage.value)

const {
  deleteOpen,
  deleteLoading,
  deleteTitle,
  deleteMessage,
  askDelete,
  confirmDelete,
} = useConfirmDelete()

const handleRemove = (company: PartnerCompany) => {
  askDelete({
    message: `Точно хотите удалить контрагента «${company.fullName}»?\nЭто действие нельзя отменить.`,
    onConfirm: async () => {
      await removeCounterparty(company.id)
      await refreshCounterparties()
    },
  })
}

const handleRefresh = async () => {
  await refreshCounterparties()
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg p-4">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Контрагенты</h2>
      <p class="text-sm text-neutral-500 mb-4">
        Общий список: покупатели, поставщики и перевозчики.
      </p>
      <ProfileCompanyList
        :companies="counterparties || []"
        :loading="loadingCounterparties"
        type="counterparty"
        :show-contracts-link="true"
        :on-remove="handleRemove"
        @refresh="handleRefresh"
      />
    </div>

    <ConfirmDeleteModal
      v-model:open="deleteOpen"
      :title="deleteTitle"
      :message="deleteMessage"
      :loading="deleteLoading"
      @confirm="confirmDelete"
    />
  </div>
</template>
