<template>
	<div>
		<UTabs v-model="activeTab" color="neutral" :items="items" size="md"
			class="max-h-screen overflow-x-auto overscroll-auto">
			<template #order="{ item }">
				<Order :data="orderData" @inputData="updateOrderData" @orderHtml="getHtml"/>

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
//Order inputs
import type { TableColumn } from '@nuxt/ui';
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import type { OrderData, ProductsInOrder } from '~/types/contracts';

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
	(e: 'orderBlob', orderDocxBlob: Blob):void
	(e: 'orderHtml', orderElement: HTMLElement | null):void
}>()

const activeTab = ref('0')
watch(
	() => activeTab.value,
	() => {
		emit('tabIndex', activeTab.value)
	},
	{ immediate: true }
)

//---Order---
const { generateDocxOrder } = useDocxGenerator()

const products: Ref<ProductsInOrder[]> = ref([
	{
		name: '',
		article: NaN,
		quantity: NaN,
		units: '',
		price: NaN,
	}
].map(product => ({ ...product, productAmount: product.price * product.quantity })))

watch(
	() => products.value,
	() => {
		products.value.map(product => product.productAmount = product.price * product.quantity )
	}, 
	{ deep: true, immediate: true }
)

const orderData: Ref<OrderData> = ref({
	innSaller: NaN,
	sallerName: '',
	companyNameSaller: '',
	urAdressSaller: '',
	mobileNumberSaller: NaN,

	buyerName: '',
	companyNameBuyer: '',
	urAdressBuyer: '',
	mobileNumberBuyer: NaN,
	orderNumber: NaN,
	orderDate: `${(new Date).getDate()}.${(new Date).getMonth()}.${(new Date).getFullYear()}`,
	comments: '',

	products,

	amount: Number(products.value.reduce((acc: number, product: ProductsInOrder) => {
		return product.productAmount + acc
	}, 0))
})

const columns: TableColumn<ProductsInOrder>[] = [
	{
		accessorKey: 'name',
		header: 'Название продукта',
	},
	{
		accessorKey: 'article',
		header: 'Артикул',
	},
	{
		accessorKey: 'quantity',
		header: 'Кол-во',
	},
	{
		accessorKey: 'units',
		header: 'Ед.изм',
	},
	{
		accessorKey: 'price',
		header: 'Цена',
	},
	{
		accessorKey: 'productAmount',
		header: 'Сумма',
	},

]

let orderDocxBlob: Blob = await generateDocxOrder(orderData.value)

watch(() => orderData,
	async () => {
		orderDocxBlob = await generateDocxOrder(orderData.value)
		emit('orderBlob', orderDocxBlob)
	},
	{ deep: true }
)

const updateOrderData = (inputData: OrderData) => {
	orderData.value = inputData
}

function getHtml(element: HTMLElement | null) {
	emit('orderHtml', element)
}
//---

</script>