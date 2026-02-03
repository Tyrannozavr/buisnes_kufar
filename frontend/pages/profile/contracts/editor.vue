<template>
	<div>
		<UTabs v-model="activeTab" color="neutral" :items="items" size="lg" variant="pill" class="max-h-[100%] overflow-y-hidden w-full" />

		<div class="flex gap-3">
			<div>
				<template v-if="activeTab === '0'">
					<div>
						<A4Page>
							<Order />
						</A4Page>
					</div>
				</template>

				<template v-if="activeTab === '1'">
					<div>
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

					</A4Page>
				</template>

				<template v-if="activeTab === '4'">
					<A4Page>

					</A4Page>
				</template>

				<template v-if="activeTab === '5'">
					<A4Page>

					</A4Page>
				</template>

				<template v-if="activeTab === '6'">
					<A4Page>
						
					</A4Page>
				</template>

				<template v-if="activeTab === '7'">
					<div>
						<A4Page>
							<DogovorUslug />
						</A4Page>
					</div>
				</template>
			</div>

			<div class="w-[23rem] justify-end">
				<EditorMenu/>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import DogovorUslug from '~/components/templates/DogovorUslug.vue'
import Bill from '~/components/templates/Bill.vue'
import SupplyContract from '~/components/templates/SupplyContract.vue'
import Order from '~/components/templates/Order.vue'
import A4Page from '~/components/ui/A4-page.vue'
import { Editor } from '~/constants/keys';


// Layout читает это состояние, чтобы знать активную вкладку (для PDF/DOCX/поиска и т.п.)
const activeTab = useTypedState(Editor.ACTIVE_TAB, () => ref('0'))

const items = [
	{
		label: 'Заказ',
		slot: 'order' as const,
	},
	{
		label: 'Счет',
		slot: 'bill' as const,
	},
	{
		label: 'Договор поставки',
		slot: 'supplyContract' as const,
	},
	{
		label: 'Сопроводительные документы',
		slot: 'accompanyingDocuments' as const,
	},
	{
		label: 'Счет-фактура',
		slot: 'invoice' as const,
	},
	{
		label: 'Договор',
		slot: 'contract' as const
	},
	{
		label: 'Акт',
		slot: 'act' as const
	},
	{
		label: 'Другие документы',
		slot: 'othersDocument' as const,
	},
]

const route = useRoute()

watch(
	() => route.fullPath,
	() => {
		if (route.hash === '#bill') {
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
</script>