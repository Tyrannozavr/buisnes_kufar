<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Продажи</h2>
        <GoodsColumns :type="'sales'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDeals } from '~/composables/useDeals'
import GoodsColumns from '~/components/tables/GoodsColumns.vue'

definePageMeta({
  layout: 'profile'
})

const { getDeals } = useDeals()

getDeals()
</script>
