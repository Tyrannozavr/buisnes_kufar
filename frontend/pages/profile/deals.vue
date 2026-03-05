<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Товары</h2>

      <UTabs :items="items" variant="link">
        <template #purchases>
          <GoodsColumns :type="'purchases'" />
        </template>

				<template #sales>
          <GoodsColumns :type="'sales'" />
        </template>
      </UTabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'
import { useDealsStore } from '~/stores/deals'
import GoodsColumns from '~/components/table/GoodsColumns.vue'

definePageMeta({
  layout: 'profile'
})

const dealsStore = useDealsStore()
dealsStore.getDeals()
const { deals } = storeToRefs(dealsStore)

const items = computed<TabsItem[]>(() => {
  const purchasesCount = deals.value.filter(deal => deal.role === 'buyer').length ?? 0
  const salesCount = deals.value.filter(deal => deal.role === 'seller').length ?? 0
  return [
    {
      label: `Закупки (${purchasesCount})`,
      description: 'Закладка товары',
      slot: 'purchases' as const,
		},
		  {
      label: `Продажи (${salesCount})`,
      description: 'Закладка товары',
      slot: 'sales' as const,
    },
  ]
})
</script>
