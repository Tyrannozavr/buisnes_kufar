<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-4 ml-4">Продажи</h2>
      <p class="text-sm text-gray-500 mb-2 ml-4">Таблица «Товары»</p>
      <GoodsColumns :type="'sales'" deal-filter="all" />
    </div>
  </div>
</template>

<script setup lang="ts">
import GoodsColumns from '~/components/tables/GoodsColumns.vue'

definePageMeta({
  layout: 'profile',
  ssr: false,
})
</script>
