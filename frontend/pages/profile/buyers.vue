<script setup lang="ts">
import type { PartnerCompany } from '~/types/company'
import ProfileCompanyList from '~/components/profile/ProfileCompanyList.vue'
import { getBuyers, removeCompanyRelation } from '~/api/company'
import { CompanyRelationType } from '~/types/company'
import { ref } from 'vue'

definePageMeta({
  layout: 'profile'
})

const page = ref(1)
const perPage = ref(10)
const {
  data: buyers,
  pending: loadingBuyers,
  refresh: refreshBuyers
} = await getBuyers(page.value, perPage.value)

const {
  deleteOpen,
  deleteLoading,
  deleteTitle,
  deleteMessage,
  askDelete,
  confirmDelete,
} = useConfirmDelete()

const handleRemoveBuyer = (buyer: PartnerCompany) => {
  askDelete({
    message: `Точно хотите удалить покупателя «${buyer.fullName}»?\nЭто действие нельзя отменить.`,
    onConfirm: async () => {
      await removeCompanyRelation(buyer.id, CompanyRelationType.BUYER)
      await refreshBuyers()
    },
  })
}

const handleRefresh = async () => {
  await refreshBuyers()
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Покупатели</h2>
      <ProfileCompanyList
        :companies="buyers || []"
        :loading="loadingBuyers"
        type="buyer"
        :onRemove="handleRemoveBuyer"
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
