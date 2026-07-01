<template>
	<div>
		<UTabs v-model="activeTab" color="neutral" :items="items" size="lg" variant="pill" class="max-h-full overflow-y-hidden w-full" />

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

definePageMeta({
  layout: 'profile'
})

const activeTab = useTypedState(Editor.ACTIVE_TAB, () => ref('0'))
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const route = useRoute()
const router = useRouter()
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
		slot: 'order' as const,
		disabled: false,
	},
	{
		label: 'Счет',
		slot: 'bill' as const,
		disabled: isItemDisabled.value.bill,
	},
	{
		label: 'Договор поставки',
		slot: 'supplyContract' as const,
		disabled: false,
	},
	{
		label: 'Сопроводительные документы',
		slot: 'accompanyingDocuments' as const,
		disabled: false,
	},
	{
		label: 'Счет-фактура',
		slot: 'invoice' as const,
		disabled: false,
	},
	{
		label: 'Договор',
		slot: 'contract' as const,
		disabled: true,
	},
	{
		label: 'Акт',
		slot: 'act' as const,
		disabled: true,
	},
	{
		label: 'Другие документы',
		slot: 'othersDocument' as const,
		disabled: true,
	},
])

watch(
	() => route.fullPath,
	() => {
		if (route.hash === '#order') {
			activeTab.value = '0'
		} else if (route.hash === '#bill') {
			activeTab.value = '1'
		} else if (route.hash === '#supplyContract') {
			activeTab.value = '2'
		} else if (route.hash === '#accompanyingDocuments') {
			activeTab.value = '3'
		} else if (route.hash === '#invoice') {
			activeTab.value = '4'
		} else if (route.hash === '#contract') {
			activeTab.value = '5'
		} else if (route.hash === '#act') {
			activeTab.value = '6'
		} else if (route.hash === '#othersDocument') {
			activeTab.value = '7'
		}
	},
	{ immediate: true }
)

watch(
  () => activeTab.value,
  () => {
    if (activeTab.value === '0') {
      router.replace({
        query: route.query,
        hash: '#order'
      })
    } else if (activeTab.value === '1') {
      router.replace({
        query: route.query,
        hash: '#bill'
      })
    } else if (activeTab.value === '2') {
      router.replace({
        query: route.query,
        hash: '#supplyContract'
      })
    } else if (activeTab.value === '3') {
      router.replace({ query: route.query, hash: '#accompanyingDocuments' })
    } else if (activeTab.value === '4') {
      router.replace({ query: route.query, hash: '#invoice' })
    } else if (activeTab.value === '7') {
      router.replace({ query: route.query, hash: '#othersDocument' })
    }
  }
)
</script>