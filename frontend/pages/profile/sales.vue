<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Продажи</h2>
      <UTabs v-model="activeTab" :items="tabItems" class="px-4 mb-2" />
      <GoodsColumns v-if="activeTab === '0'" :type="'sales'" />
      <p v-else class="px-4 pb-6 text-sm text-gray-500">
        Закладка «Услуги» — в рамках этапа 4 (70k).
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDeals } from '~/composables/useDeals'
import GoodsColumns from '~/components/tables/GoodsColumns.vue'

definePageMeta({
  layout: 'profile'
})

const activeTab = ref('0')
const tabItems = [
  { label: 'Товары' },
  { label: 'Услуги' },
]

const { getDeals } = useDeals({ role: 'seller' })
getDeals()
</script>
