<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  columns: string[]
}>()
</script>

<template>
  <div class="bg-white shadow rounded-lg p-4 space-y-3">
    <h2 class="text-lg font-medium text-gray-900">{{ title }}</h2>
    <p v-if="description" class="text-sm text-neutral-500">{{ description }}</p>
    <div class="overflow-x-auto border border-neutral-200 rounded-md">
      <table class="min-w-full text-sm">
        <thead class="bg-neutral-50 text-left">
          <tr>
            <th
              v-for="col in columns"
              :key="col"
              class="px-3 py-2 font-medium text-neutral-600 whitespace-nowrap"
            >
              {{ col }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td :colspan="columns.length" class="px-3 py-8 text-center text-neutral-400">
              Записей пока нет
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
