<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-8 text-center">
    <h1 class="text-xl font-semibold text-gray-900 mb-3">{{ title }}</h1>
    <p class="text-gray-500 max-w-md mx-auto">
      {{ description || 'Раздел в разработке.' }}
    </p>
  </div>
</template>
