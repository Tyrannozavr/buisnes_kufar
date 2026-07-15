<script setup lang="ts">
import EmptyShipmentsTable from '~/components/profile/EmptyShipmentsTable.vue'

definePageMeta({
  layout: 'profile',
  title: 'Заявки',
})
</script>

<template>
  <EmptyShipmentsTable
    title="Заявки на перевозку"
    description="Заявки (MVP). Таблица пустая до появления реальных заявок."
    :columns="['№', 'Дата', 'Откуда', 'Куда', 'Статус']"
  />
</template>
