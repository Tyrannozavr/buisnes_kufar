<template>
	<div>
		<UTabs v-model="activeTab" color="neutral" :items="items" size="md" variant="pill"
			class="max-h-screen overflow-x-auto overscroll-auto">
			<template #order="{ item }">
				<Order />

			</template>
			<template #bill="{ item }">
				<Bill />
			</template>
			<template #supplyContract="{ item }">
				<SupplyContract />
			</template>
			<template #accompanyingDocuments="{ item }">

			</template>
			<template #invoice="{ item }">

			</template>
			<template #act>

			</template>
			<template #contract>

			</template>
			<template #othersDocument="{ item }">
				<DogovorUslug />
			</template>

		</UTabs>

	</div>
</template>

<script setup lang="ts">
import DogovorUslug from '~/components/templates/DogovorUslug.vue'
import Bill from '~/components/templates/Bill.vue'
import SupplyContract from '~/components/templates/SupplyContract.vue'
import Order from '~/components/templates/Order.vue'

definePageMeta({
	layout: 'editor',
})

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
		label: 'Сопровод-е док-ты',
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
		label: 'Др. док-ты',
		slot: 'othersDocument' as const,
	},
]

const emit = defineEmits<{
	(e: 'tabIndex', activeTab: string):void,
}>()

const activeTab = ref('0')
watch(
	() => activeTab.value,
	() => {
		emit('tabIndex', activeTab.value)
	},
	{ immediate: true }
)

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
	{immediate: true}
)
</script>