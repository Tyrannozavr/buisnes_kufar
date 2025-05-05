<script setup lang="ts">
import {ref, watch, onMounted} from 'vue'
import type {Company} from '~/types/company'
import type {NavigationMenuItem} from '~/types/navigation'
import type {Announcement} from '~/types/announcement'
import PageLoader from "~/components/ui/PageLoader.vue";
import CompanyProducts from "~/components/company/CompanyProducts.vue";
import AnnouncementList from '~/components/company/AnnouncementList.vue'

const route = useRoute()
const router = useRouter()

// Fetch company data using useApi composable
const {
  data: company,
  error: companyError,
  pending: loading,
  refresh: refreshCompany
} = await useApi<Company>('/company/me')


// Fetch company announcements
const {
  data: announcements,
  pending: loadingAnnouncements,
  refresh: refreshAnnouncements,
} = await useApi<Announcement[]>('/announcements/company',
    {lazy: true}
)

const saving = ref(false)

// Get the active section from query parameter or default to 'company'
const activeSection = ref(route.query.section?.toString() || 'company')

// Update URL when activeSection changes
watch(activeSection, (newValue) => {
  router.push({
    query: {
      ...route.query,
      section: newValue
    }
  })
})

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
      active: activeSection.value === 'company',
      class: "cursor-pointer",
      onSelect: () => activeSection.value = 'company',
    },
    {
      label: 'Продукция',
      icon: 'i-heroicons-cube',
      active: activeSection.value === 'products',
      class: "cursor-pointer",
      onSelect: () => activeSection.value = 'products'
    },
    {
      label: 'Объявления',
      icon: 'i-heroicons-megaphone',
      active: activeSection.value === 'announcements',
      class: "cursor-pointer",
      onSelect: () => activeSection.value = 'announcements'
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
      onSelect: () => activeSection.value = 'partners'
    },
    {
      label: 'Поставщики',
      icon: 'i-heroicons-truck',
      to: 'suppliers',
      active: activeSection.value === 'suppliers',
      onSelect: () => activeSection.value = 'suppliers'
    },
    {
      label: 'Покупатели',
      icon: 'i-heroicons-shopping-cart',
      to: 'buyers',
      active: activeSection.value === 'buyers',
      onSelect: () => activeSection.value = 'buyers'
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
      onSelect: () => activeSection.value = 'contracts'
    },
    {
      label: 'Продажи',
      icon: 'i-heroicons-currency-dollar',
      to: 'sales',
      active: activeSection.value === 'sales',
      onSelect: () => activeSection.value = 'sales'
    },
    {
      label: 'Закупки',
      icon: 'i-heroicons-shopping-bag',
      to: 'purchases',
      active: activeSection.value === 'purchases',
      onSelect: () => activeSection.value = 'purchases'
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
      onSelect: () => activeSection.value = 'messages'
    },
    {
      label: 'Авторизация',
      icon: 'i-heroicons-key',
      to: 'auth',
      active: activeSection.value === 'auth',
      onSelect: () => activeSection.value = 'auth'
    }
  ]
])

// Watch for changes in activeSection and update the active state in navigationItems
watch(activeSection, (newValue) => {
  navigationItems.value.forEach(group => {
    group.forEach(item => {
      if (item.type !== 'label') {
        item.active = (item.to === newValue) ||
            (item.label === 'Данные компании' && newValue === 'company') ||
            (item.label === 'Продукция' && newValue === 'products') ||
            (item.label === 'Объявления' && newValue === 'announcements')
      }
    })
  })
})

// Watch for changes in route.query.section
watch(() => route.query.section, (newSection) => {
  if (newSection && typeof newSection === 'string') {
    activeSection.value = newSection
  }
}, {immediate: true})

const getSectionTitle = (section: string) => {
  // Find the section in the navigation items
  for (const group of navigationItems.value) {
    for (const item of group) {
      if ((item.to === section) ||
          (item.label === 'Данные компании' && section === 'company') ||
          (item.label === 'Продукция' && section === 'products') ||
          (item.label === 'Объявления' && section === 'announcements')) {
        return item.label
      }
    }
  }
  return section
}

const handleSaveCompany = async (data: Partial<Company>) => {
  saving.value = true
  try {
    // Update company data using useApi
    await useApi('/company/me', {
      method: 'PUT',
      body: {...company.value, ...data}
    })

    // Refresh company data
    await refreshCompany()

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

const publishAnnouncement = async (id: string) => {
  try {
    await useApi(`/announcements/${id}/publish`, {
      method: 'PUT'
    })

    await refreshAnnouncements()

    useToast().add({
      title: 'Успешно',
      description: 'Объявление опубликовано',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось опубликовать объявление',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row gap-8">
      <!-- Main Content -->
      <div class="flex-1">
        <template v-if="loading">
          <PageLoader/>
        </template>

        <template v-else-if="companyError">
          <UAlert
              color="error"
              :title="companyError.toString()"
              icon="i-heroicons-exclamation-circle"
          />
        </template>

        <template v-else-if="!company">
          <UAlert
              color="warning"
              title="Данные компании не найдены"
              description="Не удалось загрузить данные компании. Пожалуйста, попробуйте позже."
              icon="i-heroicons-exclamation-triangle"
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

          <!-- Products Section -->
          <template v-else-if="activeSection === 'products'">
            <CompanyProducts/>
          </template>

          <!-- Announcements Section -->
          <template v-else-if="activeSection === 'announcements'">
            <AnnouncementList
                :announcements="announcements || []"
                :loading="loadingAnnouncements"
                @publish="publishAnnouncement"
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
      <!-- Navigation Sidebar -->
      <div class="w-full md:w-64 flex-shrink-0">
        <UCard>
          <UNavigationMenu
              orientation="vertical"
              :items="navigationItems"
              class="data-[orientation=vertical]:w-full"
          />
        </UCard>
      </div>
    </div>
  </div>
</template>