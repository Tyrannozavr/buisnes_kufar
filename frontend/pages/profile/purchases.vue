<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Закупки</h2>

      <UTabs :items="items" variant="link">
        <template #goods>
          <GoodsColumns :type="'purchases'" />
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
  const goodsCount = deals.value.filter(deal => deal.role === 'buyer').length ?? 0
  return [
    {
      label: `Товары (${goodsCount})`,
      description: 'Закладка товары',
      slot: 'goods' as const,
      // badge: String(goodsCount)
    }
  ]
})
</script>
