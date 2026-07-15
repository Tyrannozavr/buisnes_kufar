<script setup lang="ts">
import EmptyShipmentsTable from '~/components/profile/EmptyShipmentsTable.vue'

definePageMeta({
  layout: 'profile',
  title: 'Перевозки',
})
</script>

<template>
  <EmptyShipmentsTable
    title="Перевозки"
    description="Список перевозок (MVP). Данные появятся после оформления транспортных сделок."
    :columns="['№', 'Дата', 'Контрагент', 'Маршрут', 'Состояние']"
  />
</template>
