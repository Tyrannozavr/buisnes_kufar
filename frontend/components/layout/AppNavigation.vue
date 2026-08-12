<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed, ref, watch } from 'vue'
import { useCartStore } from '~/stores/cart'
import { useChatUnreadStore } from '~/stores/chatUnread'
import { storeToRefs } from 'pinia'
import { useUserStore } from '~/stores/user'

const route = useRoute()
const cartStore = useCartStore()
const userStore = useUserStore()
const chatUnreadStore = useChatUnreadStore()
const { badgeText } = storeToRefs(chatUnreadStore)
const totalItems = computed(() => cartStore.totalUniqueItems)

const {
	navigationItems: profileNavGroups,
	loadCompany,
} = useProfileNavigation()

const profileOpen = ref(false)

const navigationItems = [
	{ name: 'Главная', path: '/' },
	{ name: 'Каталог товаров', path: '/catalog/products' },
	{ name: 'Продавцы', path: '/catalog/services' },
	{ name: 'Производители', path: '/manufacturers' },
	{ name: 'Перевозчики', path: '/service-providers' },
	{ name: 'Поиск транспорта', path: '/transport-search' },
	{ name: 'О нас', path: '/about' },
	{ name: 'Объявления', path: '/announcements' },
]

const isActive = (path: string): boolean => {
	if (path === '/' && route.path === '/') return true
	return path !== '/' && route.path.startsWith(path)
}

const props = defineProps<{
	isSidebarOpen: boolean
}>()

const emit = defineEmits<{
	'update:isSidebarOpen': [value: boolean]
}>()

const closeSidebar = () => {
	emit('update:isSidebarOpen', false)
}

watch(
	() => props.isSidebarOpen,
	async (open) => {
		if (!open) {
			profileOpen.value = false
			return
		}
		// разделы ЛК по умолчанию свёрнуты
		profileOpen.value = false
		if (userStore.isAuthenticated) {
			await loadCompany()
		}
	},
)
</script>

<template>
	<!-- Desktop Navigation -->
	<div class="bg-gray-50 border-b hidden md:block">
		<UContainer>
			<nav class="flex justify-between space-x-6 md:space-x-0 py-3">
				<UButton
					v-for="item in navigationItems"
					:key="item.path"
					:to="item.path"
					variant="ghost"
					:color="isActive(item.path) ? 'primary' : 'neutral'"
					class="text-sm"
					:class="isActive(item.path) ? 'font-medium' : ''"
				>
					{{ item.name }}
				</UButton>
			</nav>
		</UContainer>
	</div>

	<!-- Mobile Sidebar -->
	<USlideover
		:open="isSidebarOpen"
		side="left"
		class="md:hidden"
		@update:open="emit('update:isSidebarOpen', $event)"
	>
		<template #content>
			<div class="p-4 max-h-[100dvh] overflow-y-auto">
				<div class="flex justify-between items-center mb-4">
					<h2 class="text-lg font-semibold">Меню</h2>
					<UButton
						icon="i-heroicons-x-mark"
						variant="ghost"
						color="neutral"
						class="cursor-pointer"
						@click="closeSidebar"
					/>
				</div>
				<nav class="flex flex-col space-y-2">
					<div class="rounded-lg border border-gray-100 overflow-hidden">
						<button
							type="button"
							class="w-full flex items-center justify-between gap-2 px-2.5 py-2 text-left cursor-pointer"
							:class="route.path.startsWith('/profile') || profileOpen
								? 'bg-primary/10 text-primary'
								: 'bg-gray-50 text-gray-800'"
							:aria-expanded="profileOpen"
							@click="profileOpen = !profileOpen"
						>
							<span class="inline-flex items-center gap-1.5 text-sm font-medium">
								<UIcon name="i-heroicons-user-circle" class="size-5 shrink-0" />
								Личный кабинет
								<ChatUnreadBadge v-if="badgeText" :count="badgeText" />
							</span>
							<UIcon
								name="i-heroicons-chevron-down"
								class="size-4 shrink-0 transition-transform duration-200"
								:class="profileOpen ? 'rotate-180' : ''"
							/>
						</button>
						<div v-show="profileOpen" class="border-t border-gray-100 bg-white p-1.5 space-y-0.5">
							<template v-if="userStore.isAuthenticated">
								<div
									v-for="(group, groupIndex) in profileNavGroups"
									:key="groupIndex"
									class="space-y-0.5"
								>
									<p
										v-if="group.find(item => item.type === 'label')"
										class="px-2.5 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-wide text-gray-400"
									>
										{{ group.find(item => item.type === 'label')?.label }}
									</p>
									<NuxtLink
										v-for="item in group.filter(entry => entry.type !== 'label' && entry.to)"
										:key="item.to"
										:to="item.to!"
										class="flex items-center gap-2 rounded-md px-2.5 py-2 text-sm cursor-pointer"
										:class="item.active
											? 'bg-primary/10 text-primary font-medium'
											: 'text-gray-700 hover:bg-gray-50'"
										@click="closeSidebar"
									>
										<UIcon v-if="item.icon" :name="item.icon" class="size-4 shrink-0 opacity-80" />
										<span class="flex-1 min-w-0 truncate">{{ item.label }}</span>
										<ChatUnreadBadge
											v-if="item.slot === 'messages' && badgeText"
											:count="badgeText"
										/>
									</NuxtLink>
								</div>
							</template>
							<template v-else>
								<NuxtLink
									to="/auth/login?redirect=/profile"
									class="flex items-center gap-2 rounded-md px-2.5 py-2 text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
									@click="closeSidebar"
								>
									<UIcon name="i-heroicons-arrow-right-on-rectangle" class="size-4" />
									Войти в кабинет
								</NuxtLink>
							</template>
						</div>
					</div>

					<div class="border-t border-gray-100 my-1" />
					<UButton
						v-for="item in navigationItems"
						:key="item.path"
						:to="item.path"
						variant="ghost"
						:color="isActive(item.path) ? 'primary' : 'neutral'"
						class="justify-start text-sm cursor-pointer"
						:class="isActive(item.path) ? 'font-medium' : ''"
						@click="closeSidebar"
					>
						{{ item.name }}
					</UButton>
				</nav>
			</div>
		</template>
	</USlideover>
</template>
