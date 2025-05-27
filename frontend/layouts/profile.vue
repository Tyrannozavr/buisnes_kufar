<script setup lang="ts">
import type {NavigationMenuItem} from '~/types/navigation'
import Breadcrumbs from "~/components/ui/Breadcrumbs.vue"
import AppLayout from "~/components/layout/AppLayout.vue";

const route = useRoute()

// Define navigation items using the NavigationMenuItem type
const navigationItems = computed((): NavigationMenuItem[][] => [
      [
        {
          label: 'Управление компанией',
          type: 'label'
        },
        {
          label: 'Данные компании',
          icon: 'i-heroicons-building-office',
          to: '/profile',
          active: route.path === '/profile'
        },
        {
          label: 'Продукция',
          icon: 'i-heroicons-cube',
          to: '/profile/products',
          active: route.path === '/profile/products'
        },
        {
          label: 'Объявления',
          icon: 'i-heroicons-megaphone',
          to: '/profile/announcements',
          active: route.path === '/profile/announcements'
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
          to: '/profile/partners',
          active: route.path === '/profile/partners'
        },
        {
          label: 'Поставщики',
          icon: 'i-heroicons-truck',
          to: '/profile/suppliers',
          active: route.path === '/profile/suppliers'
        },
        {
          label: 'Покупатели',
          icon: 'i-heroicons-shopping-cart',
          to: '/profile/buyers',
          active: route.path === '/profile/buyers'
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
          to: '/profile/contracts',
          active: route.path === '/profile/contracts'
        },
        {
          label: 'Продажи',
          icon: 'i-heroicons-currency-dollar',
          to: '/profile/sales',
          active: route.path === '/profile/sales'
        },
        {
          label: 'Закупки',
          icon: 'i-heroicons-shopping-bag',
          to: '/profile/purchases',
          active: route.path === '/profile/purchases'
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
          to: '/profile/messages',
          active: route.path.startsWith('/profile/messages')
        },
        {
          label: 'Авторизация',
          icon: 'i-heroicons-key',
          to: '/profile/auth',
          active: route.path === '/profile/auth'
        }
      ]
    ]
)

// Get page title from route meta
const pageTitle = computed(() => {
  const title = route.meta.title
  return typeof title === 'function' ? title() : title
})

</script>

<template>
  <AppLayout>
    <div class="container mx-auto px-2 py-6 md:px-0">
      <div class="mb-6">
        <Breadcrumbs :current-page-title="pageTitle" />
      </div>
      <div class="flex flex-col md:flex-row gap-6 md:gap-8">
        <!-- Main Content -->
        <div class="w-full md:max-w-3xl md:pr-6">
          <slot/>
        </div>
        <!-- Navigation Sidebar -->
        <div class="w-full md:w-64 flex-shrink-0 md:pl-0 md:pr-4">
          <UCard class="sticky top-8 md:w-64 w-full">
            <UNavigationMenu
                orientation="vertical"
                :items="navigationItems"
                class="data-[orientation=vertical]:w-full"
            />
          </UCard>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
@media (min-width: 768px) and (max-width: 1024px) {
  .md\\:max-w-3xl {
    max-width: 768px;
  }
  .md\\:pr-6 {
    padding-right: 1.5rem;
  }
  .md\\:pr-4 {
    padding-right: 1rem;
  }
}
</style>