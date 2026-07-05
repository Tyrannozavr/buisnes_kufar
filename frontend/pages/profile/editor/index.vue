<template>
	<div>
		<UTabs
			:key="activeTab"
			v-model="activeTab"
			color="neutral"
			:items="items"
			size="lg"
			variant="pill"
			class="max-h-full overflow-y-hidden w-full"
		/>

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
						<A4Page>
							<Bill />
						</A4Page>
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
						<Invoice />
					</A4Page>
				</template>

				<template v-if="activeTab === '5'">
					<A4Page>
						<DogovorUslug />
					</A4Page>
				</template>

				<template v-if="activeTab === '6'">
					<A4Page>
						<Act />
					</A4Page>
				</template>

				<template v-if="activeTab === '7'">
					<A4Page>
						<div class="font-serif text-base text-gray-500 p-6 max-w-[210mm]">
							<p>Раздел «Другие документы» — в разработке.</p>
						</div>
					</A4Page>
				</template>
			</div>

			<div class="w-92 justify-end">
				<EditorMenu/>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import DogovorUslug from '~/components/templates/DogovorUslug.vue'
import Bill from '~/components/templates/Bill/Bill.vue'
import SupplyContract from '~/components/templates/SupplyContract/SupplyContract.vue'
import Order from '~/components/templates/Order.vue'
import AccompanyingDocuments from '~/components/templates/AccompanyingDocuments.vue'
import Invoice from '~/components/templates/Invoice.vue'
import Act from '~/components/templates/Act.vue'
import EditorMenu from '~/components/EditorMenu/index.vue'
import { Editor } from '~/constants/keys'
import A4Page from '~/components/ui/A4-page.vue'
import { useDeals } from '~/composables/useDeals'
import { useRouter } from 'vue-router'
import {
	TAB_TO_HASH,
	tabFromRoute,
	type EditorTabId,
} from '~/utils/editorNavigation'

definePageMeta({
  layout: 'profile'
})

const route = useRoute()
const router = useRouter()

const activeTab = useTypedState(Editor.ACTIVE_TAB, () =>
	ref(tabFromRoute(route.hash, route.query.tab) ?? '0'),
)
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const { getDeals, deals, findDeal } = useDeals()

getDeals()

/** Режим просмотра: покупатель read-only; поставщик редактирует. billEdit=1 — явное редактирование счёта. */
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

/** Покупатель не может перейти в режим редактирования даже программно */
watch(isDisabled, (val) => {
	if (route.query.role === 'buyer' && !val) {
		isDisabled.value = true
	}
})

const isItemDisabled = ref({
		bill: false,
		contract: false,
	})

watch(() => [
	deals.value,
	route.query.dealId,
], () => {
	const deal = findDeal(Number(route.query.dealId))
	isItemDisabled.value.bill = !deal?.billDate
	isItemDisabled.value.contract = !deal?.contractDate
}, { immediate: true, deep: true })

const items = computed(() => [
	{
		label: 'Заказ',
		value: '0',
		slot: 'order' as const,
		disabled: false,
	},
	{
		label: 'Счет',
		value: '1',
		slot: 'bill' as const,
		disabled: isItemDisabled.value.bill,
	},
	{
		label: 'Договор поставки',
		value: '2',
		slot: 'supplyContract' as const,
		disabled: false,
	},
	{
		label: 'Сопроводительные документы',
		value: '3',
		slot: 'accompanyingDocuments' as const,
		disabled: false,
	},
	{
		label: 'Счет-фактура',
		value: '4',
		slot: 'invoice' as const,
		disabled: false,
	},
	{
		label: 'Договор',
		value: '5',
		slot: 'contract' as const,
		disabled: true,
	},
	{
		label: 'Акт',
		value: '6',
		slot: 'act' as const,
		disabled: true,
	},
	{
		label: 'Другие документы',
		value: '7',
		slot: 'othersDocument' as const,
		disabled: true,
	},
])

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
		} finally {
			syncingTabToRoute.value = false
		}
	},
)
</script>