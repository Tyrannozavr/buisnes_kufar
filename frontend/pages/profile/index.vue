<script setup lang="ts">
import type { Company } from '~/types/company'
import type { NavigationMenuItem } from '@nuxt/ui'
import PageLoader from "~/components/ui/PageLoader.vue";

const { company, loading, error, fetchCompany, updateCompany } = useCompany()
const saving = ref(false)
const activeSection = ref('company')

// Define navigation items using the NavigationMenuItem type
const navigationItems = ref<NavigationMenuItem[][]>([
  [
    {
      label: 'Управление компанией',
      type: 'label'
    },
    {
      label: 'Данные компании',
      icon: 'i-heroicons-building-office',
      to: 'company',
      active: activeSection.value === 'company',
      click: () => activeSection.value = 'company'
    },
    {
      label: 'Продукция',
      icon: 'i-heroicons-cube',
      to: 'products',
      active: activeSection.value === 'products',
      click: () => activeSection.value = 'products'
    },
    {
      label: 'Объявления',
      icon: 'i-heroicons-megaphone',
      to: 'announcements',
      active: activeSection.value === 'announcements',
      click: () => activeSection.value = 'announcements'
    }
  ],
  [
    {
      label: 'Бизнес-связи',
      type: 'label'
    },
    {
      label: 'Партнеры',
      icon: 'i-heroicons-user-group',
      to: 'partners',
      active: activeSection.value === 'partners',
      click: () => activeSection.value = 'partners'
    },
    {
      label: 'Поставщики',
      icon: 'i-heroicons-truck',
      to: 'suppliers',
      active: activeSection.value === 'suppliers',
      click: () => activeSection.value = 'suppliers'
    },
    {
      label: 'Покупатели',
      icon: 'i-heroicons-shopping-cart',
      to: 'buyers',
      active: activeSection.value === 'buyers',
      click: () => activeSection.value = 'buyers'
    }
  ],
  [
    {
      label: 'Документы и финансы',
      type: 'label'
    },
    {
      label: 'Договоры',
      icon: 'i-heroicons-document-text',
      to: 'contracts',
      active: activeSection.value === 'contracts',
      click: () => activeSection.value = 'contracts'
    },
    {
      label: 'Продажи',
      icon: 'i-heroicons-currency-dollar',
      to: 'sales',
      active: activeSection.value === 'sales',
      click: () => activeSection.value = 'sales'
    },
    {
      label: 'Закупки',
      icon: 'i-heroicons-shopping-bag',
      to: 'purchases',
      active: activeSection.value === 'purchases',
      click: () => activeSection.value = 'purchases'
    }
  ],
  [
    {
      label: 'Коммуникации',
      type: 'label'
    },
    {
      label: 'Сообщения',
      icon: 'i-heroicons-chat-bubble-left-right',
      to: 'messages',
      active: activeSection.value === 'messages',
      click: () => activeSection.value = 'messages'
    },
    {
      label: 'Авторизация',
      icon: 'i-heroicons-key',
      to: 'auth',
      active: activeSection.value === 'auth',
      click: () => activeSection.value = 'auth'
    }
  ]
])

// Watch for changes in activeSection and update the active state in navigationItems
watch(activeSection, (newValue) => {
  navigationItems.value.forEach(group => {
    group.forEach(item => {
      if (item.to) {
        item.active = item.to === newValue
      }
    })
  })
})

const getSectionTitle = (section: string) => {
  // Find the section in the navigation items
  for (const group of navigationItems.value) {
    for (const item of group) {
      if (item.to === section) {
        return item.label
      }
    }
  }
  return section
}

const handleSaveCompany = async (data: Partial<Company>) => {
  saving.value = true
  try {
    await updateCompany(data)
    useToast().add({
      title: 'Успешно',
      description: 'Данные компании обновлены',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось обновить данные компании',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

// Fetch company data on page load
onMounted(() => {
  fetchCompany()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row gap-8">
      <!-- Navigation Menu -->
      <div class="w-full md:w-64 flex-shrink-0">
        <UCard>
          <UNavigationMenu
            orientation="vertical"
            :items="navigationItems"
            class="data-[orientation=vertical]:w-full"
          />
        </UCard>
      </div>

      <!-- Main Content -->
      <div class="flex-1">
        <template v-if="loading">
          <PageLoader
            size="lg"
            text="Загрузка данных компании..."
          />
        </template>

        <template v-else-if="error">
          <UAlert
              color="error"
              :title="error"
              icon="i-heroicons-exclamation-circle"
          />
        </template>

        <template v-else>
          <!-- Company Data Section -->
          <template v-if="activeSection === 'company'">
            <CompanyDataForm
                :company="company"
                :loading="saving"
                @save="handleSaveCompany"
            />
          </template>

          <!-- Other sections will be added here -->
          <template v-else>
            <UCard>
              <template #header>
                <h3 class="text-xl font-semibold">
                  {{ getSectionTitle(activeSection) }}
                </h3>
              </template>
              <p class="text-gray-500">
                Раздел находится в разработке
              </p>
            </UCard>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>