<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Закупки</h2>
      <UTabs
        v-model="activeTab"
        :items="tabItems"
        color="primary"
        variant="pill"
        :content="false"
        class="px-4 mb-2"
        :ui="{
          indicator: 'hidden',
          trigger:
            'data-[state=active]:bg-primary-500 data-[state=active]:text-white rounded-md data-[state=inactive]:text-gray-600 hover:data-[state=inactive]:text-gray-900',
        }"
      />
      <GoodsColumns v-if="activeTab === '0'" :type="'purchases'" deal-filter="Товары" />
      <GoodsColumns v-else :type="'purchases'" deal-filter="Услуги" />
    </div>
  </div>
</template>

<script setup lang="ts">
import GoodsColumns from '~/components/tables/GoodsColumns.vue'

definePageMeta({
  layout: 'profile',
  ssr: false,
})

const activeTab = ref('0')
const tabItems = [
  { label: 'Товары' },
  { label: 'Услуги' },
]
</script>
