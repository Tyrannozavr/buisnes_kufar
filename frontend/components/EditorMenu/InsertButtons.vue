<script setup lang="ts">
import { useRouter } from 'nuxt/app'; 
import { Editor } from '~/constants/keys';
import { useDeals } from '~/composables/useDeals';

const toast = useToast()
const router = useRouter()
const { lastDeal } = useDeals()
const isDisabled = useTypedState(Editor.IS_DISABLED)

const { isCancelChanges } = defineProps<{
  isCancelChanges: {
    sales: boolean
    purchases: boolean
  }
}>()

const insertLastPurchases = (): void => {
	const lastDealId = lastDeal?.value?.purchases?.dealId
	router.replace({ query: { role: 'buyer', dealId: String(lastDealId) } })

	if (!lastDealId) {
		toast.add({
			title: 'Нет последней закупки',
			color: 'warning',
		})
		return
	}
}

const insertLastSales = (): void => {
	const lastDealId = lastDeal?.value?.sales?.dealId
	router.replace({ query: { role: 'seller', dealId: String(lastDealId) } })

	if (!lastDealId) {
		toast.add({
			title: 'Нет последней продажи',
			color: 'warning',
		})
		return
	}
}

watch(() => isCancelChanges,
  () => {
    if (isCancelChanges.sales) {
      insertLastSales()
    }
    if (isCancelChanges.purchases) {
      insertLastPurchases()
    }
  }, { deep: true }
)
</script>

<template>
  <div class="w-full">
    <UCollapsible>
      <UButton label="Заполнить данными" icon="i-lucide-file-input" class="w-full justify-center"
        :disabled="!isDisabled" />

      <template #content>
        <div class="flex gap-2 mt-4 justify-center">
          <div class="w-1/2">
            <UButton label="Последняя закупка" color="neutral" variant="subtle" class="w-full justify-center py-2"
              @click="insertLastPurchases" />
          </div>
          <div class="w-1/2">
            <UButton label="Последняя продажа" color="neutral" variant="subtle" class="w-full justify-center py-2"
              @click="insertLastSales" />
          </div>
        </div>
      </template>
    </UCollapsible>
  </div>
</template>