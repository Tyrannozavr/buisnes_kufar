<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  label: string
  path: string
}

const props = defineProps({
  currentPageTitle: {
    type: String,
    default: ''
  }
})

const route = useRoute()
const breadcrumbs = ref<BreadcrumbItem[]>([])

function getLabel(path: string): string {
  const labels: Record<string, string> = {
    'profile': 'Профиль',
    'announcements': 'Объявления',
    'products': 'Продукция',
    'partners': 'Партнеры',
    'suppliers': 'Поставщики',
    'buyers': 'Покупатели',
    'contracts': 'Договоры',
    'sales': 'Продажи',
    'purchases': 'Закупки',
    'messages': 'Сообщения',
    'auth': 'Авторизация',
    'create': 'Создание',
    'edit': 'Редактирование',
  }

  return labels[path] || path
}

async function updateBreadcrumbs() {
  const paths = route.path.split('/').filter(Boolean)
  const items: BreadcrumbItem[] = []

  // Add home item
  items.push({ label: 'Главная', path: '/' })

  // Check if we should hide the last breadcrumb
  const hideLastItem = route.meta.hideLastBreadcrumb === true
  const pathsToProcess = hideLastItem ? paths.slice(0, -1) : paths

  for (let i = 0; i < pathsToProcess.length; i++) {
    const path = pathsToProcess[i]
    const fullPath = '/' + paths.slice(0, i + 1).join('/')

    // If this is the last item and we have a custom page title, use it
    if (i === pathsToProcess.length - 1 && props.currentPageTitle) {
      items.push({ label: props.currentPageTitle, path: fullPath })
    } else {
      let label = getLabel(path)
      items.push({ label, path: fullPath })
    }
  }

  breadcrumbs.value = items
}

watch(() => route.path, updateBreadcrumbs, { immediate: true })
watch(() => props.currentPageTitle, updateBreadcrumbs)
watch(() => route.meta, updateBreadcrumbs, { deep: true })
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