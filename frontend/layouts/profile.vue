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

/** В открытом диалоге (/profile/messages/:id) боковое меню ЛК скрываем — место под чат. */
const hideProfileSidebar = computed(() =>
	/^\/profile\/messages\/[^/]+$/.test(route.path) && route.path !== '/profile/messages/new',
)

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
      label: 'Контрагенты',
      icon: 'i-heroicons-user-group',
      to: '/profile/partners',
      active: route.path === '/profile/partners' || route.path === '/profile/counterparties'
    },
    {
      label: 'Перевозчики',
      icon: 'i-heroicons-truck',
      to: '/profile/carriers',
      active: route.path === '/profile/carriers'
    },
  ]

  if (!isLogistics.value) {
    businessBlock.push(
      {
        label: 'Поставщики',
        icon: 'i-heroicons-building-storefront',
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

  const shipmentsBlock: NavigationMenuItem[] = [
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
  ]
  // Избранное: клиент — ТС; перевозчик/экспедитор — заявки (ТЗ_Перевозчик §G)
  shipmentsBlock.push({
    label: 'Избранное',
    icon: 'i-heroicons-star',
    to: '/profile/shipment-favorites',
    active: route.path === '/profile/shipment-favorites'
  })

  const items: NavigationMenuItem[][] = [companyBlock, businessBlock, docsBlock, shipmentsBlock]

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

const mobileNavOpen = ref(false)

const currentNavLabel = computed(() => {
	for (const group of navigationItems.value) {
		for (const item of group) {
			if (item.type === 'label' || !item.to) continue
			if (item.active) return item.label
		}
	}
	const title = pageTitle.value
	return typeof title === 'string' && title ? title : 'Разделы'
})

watch(
	() => route.fullPath,
	() => {
		mobileNavOpen.value = false
	},
)

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
			<div class="mb-4 md:mb-6">
				<Breadcrumbs :current-page-title="pageTitle" />
			</div>

			<!-- Mobile: sticky bar разделов (сайдбар снизу скрыт) -->
			<div
				v-if="!hideProfileSidebar"
				class="md:hidden sticky top-[72px] z-40 -mx-2 px-2 mb-4"
			>
				<button
					type="button"
					class="w-full flex items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white/95 backdrop-blur px-3 py-2.5 text-left shadow-sm cursor-pointer"
					@click="mobileNavOpen = true"
				>
					<span class="min-w-0">
						<span class="block text-xs text-gray-500">Раздел ЛК</span>
						<span class="block truncate font-medium text-gray-900">{{ currentNavLabel }}</span>
					</span>
					<span class="relative shrink-0 inline-flex items-center gap-1.5 text-sm text-primary-600 font-medium">
						<ChatUnreadBadge v-if="badgeText" :count="badgeText" />
						<span>Сменить</span>
						<UIcon name="i-heroicons-chevron-down" class="size-4" />
					</span>
				</button>
			</div>

			<UModal
				v-model:open="mobileNavOpen"
				title="Разделы личного кабинета"
				description="Выберите раздел для перехода"
				:ui="{ content: 'sm:max-w-md w-[calc(100%-1.5rem)]' }"
			>
				<template #body>
					<nav class="max-h-[min(70vh,32rem)] overflow-y-auto -mx-1 px-1 space-y-4">
						<div
							v-for="(group, groupIndex) in navigationItems"
							:key="groupIndex"
							class="space-y-1"
						>
							<p
								v-if="group.find(item => item.type === 'label')"
								class="px-2 pt-1 text-xs font-semibold uppercase tracking-wide text-gray-400"
							>
								{{ group.find(item => item.type === 'label')?.label }}
							</p>
							<NuxtLink
								v-for="item in group.filter(entry => entry.type !== 'label' && entry.to)"
								:key="item.to"
								:to="item.to!"
								class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors cursor-pointer"
								:class="item.active
									? 'bg-primary-50 text-primary-700 font-medium ring-1 ring-primary-100'
									: 'text-gray-700 hover:bg-gray-50'"
								@click="mobileNavOpen = false"
							>
								<UIcon
									v-if="item.icon"
									:name="item.icon"
									class="size-5 shrink-0 opacity-80"
								/>
								<span class="flex-1 min-w-0 truncate">{{ item.label }}</span>
								<ChatUnreadBadge
									v-if="item.slot === 'messages' && badgeText"
									:count="badgeText"
								/>
								<UIcon
									v-if="item.active"
									name="i-heroicons-check"
									class="size-4 shrink-0 text-primary-600"
								/>
							</NuxtLink>
						</div>
					</nav>
				</template>
				<template #footer>
					<div class="flex justify-end">
						<UButton
							label="Закрыть"
							color="neutral"
							variant="outline"
							class="cursor-pointer"
							@click="mobileNavOpen = false"
						/>
					</div>
				</template>
			</UModal>

			<!-- Альтернативное меню навигации ??? -->
			<div v-if="alternativeLayout()" class="flex flex-col md:flex-col gap-6 md:gap-8">
				<div class="hidden md:flex justify-end px-2">
					<UButton
						to="/profile/messages"
						color="neutral"
						variant="soft"
						icon="i-heroicons-chat-bubble-left-right"
						class="relative cursor-pointer"
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
				<div class="w-full md:max-w-full">
					<slot />
				</div>
			</div>

			<div v-else class="flex flex-col md:flex-row gap-6 md:gap-8">
				<!-- Main Content -->
				<div
					class="w-full md:pr-6"
					:class="hideProfileSidebar ? 'md:max-w-full' : 'md:max-w-3xl'"
				>
					<slot />
				</div>
				<!-- Desktop sidebar — на мобилке скрыт, вместо него sticky bar -->
				<div
					v-if="!hideProfileSidebar"
					class="hidden md:block w-full md:w-64 shrink-0 md:pl-0 md:pr-4"
				>
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
