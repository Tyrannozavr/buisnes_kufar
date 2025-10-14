<template>
	<div>
		<UTabs v-model="activeTab" color="neutral" :items="items" size="md"
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
		label: 'Сопровидительный документы',
		slot: 'accompanyingDocuments' as const,
	},
	{
		label: 'Счет-фактура',
		slot: 'invoice' as const,
	},
	{
		label: 'Другие документы',
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
</script>