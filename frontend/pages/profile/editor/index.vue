<template>
	<div>
		<div
			v-if="!isDealReady"
			class="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-neutral-500"
		>
			<UIcon
				v-if="dealLoadPending"
				name="i-lucide-loader-circle"
				class="size-10 animate-spin text-emerald-600"
			/>
			<p v-if="dealLoadPending">Загрузка сделки…</p>
			<p v-else-if="dealLoadFailed" class="text-center text-amber-700">
				Не удалось загрузить сделку. Проверьте ссылку или обновите страницу.
			</p>
		</div>

		<template v-else>
		<nav
			class="mb-3 flex w-full flex-wrap gap-1 rounded-lg bg-elevated p-1"
			aria-label="Документы сделки"
		>
			<UTooltip
				v-for="item in items"
				:key="item.value"
				:text="item.disabledReason || ''"
				:disabled="!item.disabled || !item.disabledReason"
			>
				<span
					class="inline-flex"
					:class="{ 'cursor-not-allowed': item.disabled && item.disabledReason }"
				>
					<button
						type="button"
						:disabled="item.disabled"
						:aria-current="activeTab === item.value ? 'page' : undefined"
						class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-40"
						:class="
							activeTab === item.value
								? 'bg-inverted text-inverted shadow-sm'
								: 'text-muted hover:text-default'
						"
						@click="onTabClick(item)"
					>
						{{ item.label }}
					</button>
				</span>
			</UTooltip>
		</nav>

		<div class="flex gap-3">
			<div>
				<template v-if="activeTab === '0'">
					<div id="order">
						<A4Page>
							<Order />
						</A4Page>
					</div>
				</template>

				<template v-if="activeTab === '1'">
					<div id="bill">
						<A4Page v-if="hasBill">
							<Bill />
						</A4Page>
						<div
							v-else
							class="flex min-h-[420px] w-[210mm] max-w-full flex-col items-center justify-center gap-4 rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center"
						>
							<p class="text-neutral-600 max-w-md">
								Счёт для этой сделки ещё не создан.
							</p>
							<UButton
								v-if="!isBuyerRole"
								label="Создать счет"
								icon="i-lucide-file-plus"
								color="primary"
								size="lg"
								:loading="isCreateBillBusy"
								:disabled="isCreateBillBusy"
								@click="onCreateBillFromTab"
							/>
							<p v-else class="text-sm text-neutral-500">
								Дождитесь, пока поставщик создаст счёт.
							</p>
						</div>
					</div>
				</template>

				<template v-if="activeTab === '2'">
					<A4Page>
						<SupplyContract />
					</A4Page>
				</template>

				<template v-if="activeTab === '3'">
					<A4Page>
						<AccompanyingDocuments />
					</A4Page>
				</template>

				<template v-if="activeTab === '4'">
					<A4Page>
						<div class="flex min-h-[320px] flex-col items-center justify-center gap-3 p-8 text-center text-neutral-500">
							<p>Счёт-фактура ещё не создана.</p>
							<p class="text-sm">Раздел в разработке.</p>
						</div>
					</A4Page>
				</template>

				<template v-if="activeTab === '5'">
					<A4Page>
						<div class="flex min-h-[320px] flex-col items-center justify-center gap-3 p-8 text-center text-neutral-500">
							<p>Договор услуг ещё не создан.</p>
							<p class="text-sm">Раздел в разработке.</p>
						</div>
					</A4Page>
				</template>

				<template v-if="activeTab === '6'">
					<A4Page>
						<div class="flex min-h-[320px] flex-col items-center justify-center gap-3 p-8 text-center text-neutral-500">
							<p>Акт ещё не создан.</p>
							<p class="text-sm">Раздел в разработке.</p>
						</div>
					</A4Page>
				</template>

				<template v-if="activeTab === '7'">
					<A4Page>
						<div class="flex min-h-[320px] flex-col items-center justify-center gap-3 p-8 text-center text-neutral-500">
							<p>Другие документы — в разработке.</p>
						</div>
					</A4Page>
				</template>
			</div>

			<div v-if="showEditorMenu" class="w-92 justify-end">
				<EditorMenu/>
			</div>
		</div>

		<CreateBillFromSalesDialogs />
		</template>
	</div>
</template>

<script setup lang="ts">
import Bill from '~/components/templates/Bill/Bill.vue'
import SupplyContract from '~/components/templates/SupplyContract/SupplyContract.vue'
import Order from '~/components/templates/Order.vue'
import AccompanyingDocuments from '~/components/templates/AccompanyingDocuments.vue'
import EditorMenu from '~/components/EditorMenu/index.vue'
import CreateBillFromSalesDialogs from '~/components/EditorMenu/CreateBillFromSalesDialogs.vue'
import { Editor } from '~/constants/keys'
import A4Page from '~/components/ui/A4-page.vue'
import { useDeals } from '~/composables/useDeals'
import { useCreateBillFromSales } from '~/composables/useCreateBillFromSales'
import { useRouter } from 'vue-router'
import {
	TAB_TO_HASH,
	tabFromRoute,
	type EditorTabId,
} from '~/utils/editorNavigation'

definePageMeta({
	layout: 'profile',
})

const route = useRoute()
const router = useRouter()

const parseDealId = (): number => {
	const raw = route.query.dealId
	const id = Number(Array.isArray(raw) ? raw[0] : raw)
	return Number.isFinite(id) && id > 0 ? id : 0
}

const dealId = computed(() => parseDealId())
const dealLoadPending = ref(true)
const dealLoadFailed = ref(false)
const isDealReady = computed(() => !dealLoadPending.value && !dealLoadFailed.value)

const activeTab = useTypedState(Editor.ACTIVE_TAB, () =>
	ref(tabFromRoute(route.hash, route.query.tab) ?? '0'),
)
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const { ensureDealLoaded, findDeal } = useDeals()
const { startCreateBillByDealId, isBusy: isCreateBillBusy } = useCreateBillFromSales()

const loadEditorDeal = async (id: number): Promise<void> => {
	dealLoadPending.value = true
	dealLoadFailed.value = false
	if (!id) {
		dealLoadFailed.value = true
		dealLoadPending.value = false
		return
	}
	const ok = await ensureDealLoaded(id)
	dealLoadFailed.value = !ok
	dealLoadPending.value = false
	if (ok) {
		loadDealTrigger.value++
	}
}

await loadEditorDeal(parseDealId())

watch(dealId, (id) => {
	void loadEditorDeal(id)
})

/** Режим просмотра при смене сделки/вкладки. billEdit=1 — явное редактирование счёта (продавец). */
watch(
	() => [route.query.dealId, route.query.role, route.hash, route.query.billEdit],
	() => {
		if (route.query.billEdit === '1') {
			isDisabled.value = false
			loadDealTrigger.value++
			const query = { ...route.query }
			delete query.billEdit
			router.replace({ query, hash: route.hash })
			return
		}
		isDisabled.value = true
	},
	{ immediate: true },
)

/** §3.3: покупатель редактирует только вкладку «Заказ»; счёт/договор — просмотр */
watch([isDisabled, activeTab], ([disabled, tab]) => {
	if (route.query.role !== 'buyer' || disabled) return
	if (tab !== '0') {
		isDisabled.value = true
	}
})

const currentDeal = computed(() => findDeal(dealId.value))
const hasBill = computed(() =>
	Boolean(currentDeal.value?.billDate || currentDeal.value?.bill?.number),
)
const isBuyerRole = computed(() => route.query.role === 'buyer')

/** Пустая вкладка «Счет» без меню — только кнопка создания. */
const showEditorMenu = computed(() => {
	if (activeTab.value === '1' && !hasBill.value) return false
	if (['4', '5', '6', '7'].includes(activeTab.value)) return false
	return true
})

const billTabDisabledForBuyer = computed(() => isBuyerRole.value && !hasBill.value)

const billTabDisabledReason = computed(() => {
	if (!billTabDisabledForBuyer.value) return ''
	return 'Счёт ещё не создан. Вкладка откроется после того, как поставщик создаст счёт.'
})

const items = computed(() => [
	{
		label: 'Заказ',
		value: '0' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
	{
		label: 'Счет',
		value: '1' as EditorTabId,
		disabled: billTabDisabledForBuyer.value,
		disabledReason: billTabDisabledReason.value,
	},
	{
		label: 'Договор поставки',
		value: '2' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
	{
		label: 'Сопроводительные документы',
		value: '3' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
	{
		label: 'Счет-фактура',
		value: '4' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
	{
		label: 'Договор',
		value: '5' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
	{
		label: 'Акт',
		value: '6' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
	{
		label: 'Другие документы',
		value: '7' as EditorTabId,
		disabled: false,
		disabledReason: '',
	},
])

const onTabClick = (item: { value: EditorTabId; disabled: boolean }) => {
	if (item.disabled) return
	activeTab.value = item.value
}

const onCreateBillFromTab = async () => {
	await startCreateBillByDealId(dealId.value)
}

/** Пока обновляем URL из вкладки — не откатывать activeTab по старому ?tab= */
const syncingTabToRoute = ref(false)

const routeTabQuery = (): string | undefined => {
	const tab = route.query.tab
	return Array.isArray(tab) ? tab[0] : tab
}

watch(
	() => [route.hash, route.query.tab] as const,
	() => {
		if (syncingTabToRoute.value) return
		const tab = tabFromRoute(route.hash, route.query.tab)
		// null = hash и ?tab временно не совпадают — не трогаем activeTab
		if (tab && activeTab.value !== tab) {
			activeTab.value = tab
		}
	},
	{ immediate: true },
)

watch(
	() => activeTab.value,
	async (tab: EditorTabId) => {
		const hash = TAB_TO_HASH[tab]
		const tabQuery = tab === '0' ? 'order' : tab === '1' ? 'bill' : undefined
		const nextQuery = { ...route.query } as Record<string, string>
		if (tabQuery) {
			nextQuery.tab = tabQuery
		} else {
			delete nextQuery.tab
		}
		const currentTabQuery = routeTabQuery()
		if (!hash || (route.hash === hash && currentTabQuery === nextQuery.tab)) {
			return
		}
		syncingTabToRoute.value = true
		try {
			await router.replace({ query: nextQuery, hash })
			await nextTick()
		} finally {
			syncingTabToRoute.value = false
		}
	},
)
</script>
