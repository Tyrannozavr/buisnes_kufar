<script setup lang="ts">
import EmptyShipmentsTable from '~/components/profile/EmptyShipmentsTable.vue'

definePageMeta({
  layout: 'profile',
  title: 'Избранное',
})
</script>

<template>
  <EmptyShipmentsTable
    title="Избранное"
    description="Избранные перевозчики и объявления (MVP)."
    :columns="['Название', 'Тип', 'Город', '']"
  />
</template>
