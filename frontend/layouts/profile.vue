<script setup lang="ts">
import type { NavigationMenuItem } from '~/types/navigation'
import Breadcrumbs from "~/components/ui/Breadcrumbs.vue"
import AppLayout from "~/components/layout/AppLayout.vue";
import { useChatUnreadStore } from '~/stores/chatUnread'
import { storeToRefs } from 'pinia'
import { getMyCompany } from '~/api/companyOwner'
import { isLogisticsTradeActivity } from '~/types/company'

const route = useRoute()
const chatUnreadStore = useChatUnreadStore()
const { badgeText } = storeToRefs(chatUnreadStore)

const tradeActivity = ref<string | null>(null)
const companyLoaded = ref(false)

onMounted(async () => {
  try {
    const company = await getMyCompany()
    tradeActivity.value = company?.trade_activity ?? null
  } catch {
    tradeActivity.value = null
  } finally {
    companyLoaded.value = true
  }
})

const isLogistics = computed(() => isLogisticsTradeActivity(tradeActivity.value))

const navigationItems = computed((): NavigationMenuItem[][] => {
  const companyBlock: NavigationMenuItem[] = [
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
  ]

  if (isLogistics.value) {
    companyBlock.push(
      {
        label: 'Транспорт',
        icon: 'i-heroicons-truck',
        to: '/profile/transport',
        active: route.path === '/profile/transport'
      },
      {
        label: 'Водители',
        icon: 'i-heroicons-identification',
        to: '/profile/drivers',
        active: route.path === '/profile/drivers'
      },
    )
  } else {
    companyBlock.push({
      label: 'Продукция',
      icon: 'i-heroicons-cube',
      to: '/profile/products',
      active: route.path === '/profile/products'
    })
  }

  companyBlock.push({
    label: 'Объявления',
    icon: 'i-heroicons-megaphone',
    to: '/profile/announcements',
    active: route.path === '/profile/announcements'
  })

  const businessBlock: NavigationMenuItem[] = [
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
  ]

  if (!isLogistics.value) {
    businessBlock.push(
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
      },
    )
  }

  const docsBlock: NavigationMenuItem[] = [
    {
      label: 'Документы и финансы',
      type: 'label'
    },
    {
      label: 'Документы',
      icon: 'i-heroicons-document-text',
      to: '/profile/documents',
      active: route.path === '/profile/documents'
    },
  ]

  if (!isLogistics.value) {
    docsBlock.push(
      {
        label: 'Договоры',
        icon: 'i-heroicons-document-duplicate',
        to: '/profile/contracts',
        active: route.path === '/profile/contracts'
      },
      {
        label: 'Редактор документов',
        icon: 'i-heroicons-pencil-square',
        to: '/profile/editor',
        active: route.path === '/profile/editor'
      },
      {
        label: 'Закупки',
        icon: 'i-heroicons-shopping-bag',
        to: '/profile/purchases',
        active: route.path === '/profile/purchases'
      },
      {
        label: 'Продажи',
        icon: 'i-heroicons-banknotes',
        to: '/profile/sales',
        active: route.path.startsWith('/profile/sales')
      },
    )
  }

  const items: NavigationMenuItem[][] = [companyBlock, businessBlock, docsBlock]

  if (isLogistics.value) {
    items.push([
      {
        label: 'Перевозки',
        type: 'label'
      },
      {
        label: 'Перевозки',
        icon: 'i-heroicons-map',
        to: '/profile/shipments',
        active: route.path === '/profile/shipments'
      },
      {
        label: 'Заявки',
        icon: 'i-heroicons-clipboard-document-list',
        to: '/profile/shipment-requests',
        active: route.path === '/profile/shipment-requests'
      },
      {
        label: 'Избранное',
        icon: 'i-heroicons-star',
        to: '/profile/shipment-favorites',
        active: route.path === '/profile/shipment-favorites'
      },
    ])
  }

  items.push([
    {
      label: 'Управление',
      type: 'label'
    },
    {
      label: 'Сообщения',
      icon: 'i-heroicons-chat-bubble-left-right',
      to: '/profile/messages',
      active: route.path.startsWith('/profile/messages'),
      slot: 'messages',
    },
    {
      label: 'Авторизация',
      icon: 'i-heroicons-key',
      to: '/profile/auth',
      active: route.path === '/profile/auth'
    },
    {
      label: 'Администрирование',
      icon: 'i-heroicons-users',
      to: '/profile/administration',
      active: route.path === '/profile/administration'
    },
  ])

  return items
})

// Get page title from route meta
const pageTitle = computed(() => {
	const title = route.meta.title
	return typeof title === 'function' ? title() : title
})

// Полноширинный контент без бокового меню: Закупки, Продажи и Редактор документов
const alternativeLayout = () =>
  route.path === '/profile/sales' ||
	route.path === '/profile/purchases' ||
	route.path === '/profile/editor'

const FORBIDDEN_FOR_LOGISTICS = [
  '/profile/products',
  '/profile/suppliers',
  '/profile/buyers',
  '/profile/sales',
  '/profile/purchases',
]

watch(
  [isLogistics, companyLoaded, () => route.path],
  ([logistics, loaded, path]) => {
    if (!loaded || !logistics) return
    if (FORBIDDEN_FOR_LOGISTICS.some((p) => path === p || path.startsWith(`${p}/`))) {
      navigateTo('/profile')
    }
  },
  { immediate: true },
)
</script>

<template>
	<AppLayout>
		<div class="container mx-auto px-2 py-6 md:px-0">
			<div class="mb-6">
				<Breadcrumbs :current-page-title="pageTitle" />
			</div>

			<!-- Альтернативное меню навигации ??? -->
			<div v-if="alternativeLayout()" class="flex flex-col md:flex-col gap-6 md:gap-8">
				<div class="flex justify-end px-2">
					<UButton
						to="/profile/messages"
						color="neutral"
						variant="soft"
						icon="i-heroicons-chat-bubble-left-right"
						class="relative"
					>
						Сообщения
						<ChatUnreadBadge
							v-if="badgeText"
							:count="badgeText"
							class="absolute -top-1 -right-1 pointer-events-none"
						/>
					</UButton>
				</div>
				<!-- Main Content -->
				<div class="w-full md:max-w-full order-2">
					<slot />
				</div>
				<!-- Navigation Sidebar -->
				<div class="w-lg md:w-full shrink-0 order-1">
					<!-- <UNavigationMenu arrow orientation="horizontal" content-orientation="vertical" :items="alternativeNavigationItems" /> -->
				</div>
			</div>

			<div v-else class="flex flex-col md:flex-row gap-6 md:gap-8">
				<!-- Main Content -->
				<div class="w-full md:max-w-3xl md:pr-6">
					<slot />
				</div>
				<!-- Navigation Sidebar -->
				<div class="w-full md:w-64 shrink-0 md:pl-0 md:pr-4">
					<UCard class="sticky top-8 md:w-64 w-full">
						<UNavigationMenu orientation="vertical" :items="navigationItems"
							class="data-[orientation=vertical]:w-full">
							<template #messages-trailing>
								<ChatUnreadBadge v-if="badgeText" :count="badgeText" />
							</template>
						</UNavigationMenu>
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
