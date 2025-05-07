<script setup lang="ts">
const route = useRoute()

const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean)
  const items = paths.map((path, index) => {
    const fullPath = '/' + paths.slice(0, index + 1).join('/')
    return {
      label: getLabel(path),
      path: fullPath
    }
  })
  return items
})

function getLabel(path: string): string {
  const labels: Record<string, string> = {
    profile: 'Профиль',
    products: 'Продукция',
    announcements: 'Объявления',
    partners: 'Партнеры',
    suppliers: 'Поставщики',
    buyers: 'Покупатели',
    contracts: 'Договоры',
    sales: 'Продажи',
    purchases: 'Закупки',
    messages: 'Сообщения',
    auth: 'Авторизация'
  }
  return labels[path] || path
}
</script>

<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2">
      <li v-for="(item, index) in breadcrumbs" :key="item.path" class="flex items-center">
        <div v-if="index > 0" class="mx-2 text-gray-400">/</div>
        <NuxtLink
          :to="item.path"
          class="text-sm font-medium"
          :class="[
            index === breadcrumbs.length - 1
              ? 'text-gray-500'
              : 'text-primary-600 hover:text-primary-700'
          ]"
        >
          {{ item.label }}
        </NuxtLink>
      </li>
    </ol>
  </nav>
</template> 