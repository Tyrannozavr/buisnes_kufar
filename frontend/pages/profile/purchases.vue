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
import { usePurchasesStore } from '~/stores/purchases'
import { usePurchasesApi } from '~/api/purchases'
import GoodsColumns from '~/components/table/GoodsColumns.vue'

definePageMeta({
  layout: 'profile'
})

const purchasesStore = usePurchasesStore()
const purchasesApi = usePurchasesApi()
const { purchases } = storeToRefs(purchasesStore)

purchasesStore.getDeals(purchasesApi)

const items = computed<TabsItem[]>(() => {
  const goodsCount = purchases.value.goodsDeals?.length ?? 0
  return [
    {
      label: `Товары (${goodsCount})`,
      description: 'Закладка товары',
      slot: 'goods' as const,
      badge: String(goodsCount)
    }
  ]
})
</script>
