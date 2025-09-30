<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import type { OrderData, ProductsInOrder } from '~/types/contracts';

const { generateDocxOrder, downloadBlob } = useDocxGenerator()

const props = defineProps<{
	data: OrderData
}>()
console.log('Props: ',props)


const emit = defineEmits<{
	(e: 'inputData', orderData: OrderData): void
}>()

const products: ProductsInOrder[] = props.data.products.map(product => ({
			name: product.name,
			article: product.article,
			quantity: product.quantity,
			units: product.units,
			price: product.price,
			productAmount: product.productAmount,
}))

const orderData: Ref<OrderData> = ref({
	innSaller: props.data.innSaller,
	sallerName: props.data.sallerName,
	companyNameSaller: props.data.companyNameSaller,
	urAdressSaller: props.data.urAdressSaller,
	mobileNumberSaller: props.data.mobileNumberSaller,

	buyerName: props.data.buyerName,
	companyNameBuyer: props.data.companyNameBuyer,
	urAdressBuyer: props.data.urAdressBuyer,
	mobileNumberBuyer: props.data.mobileNumberBuyer,
	orderNumber: props.data.orderNumber,
	orderDate: props.data.orderDate,
	comments: props.data.comments,

	products,

	amount: props.data.amount,
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

let docxBlob: Blob = await generateDocxOrder(orderData.value)

watch(() => orderData.value,
	async () => {
		docxBlob = await generateDocxOrder(orderData.value)

		emit('inputData', orderData.value)
	},
	{deep: true}
)

//заглушка
const data = ref([

  // {
  //   id: '4600',
  //   date: '2024-03-11T15:30:00',
  //   status: 'paid',
  //   email: 'james.anderson@example.com',
  //   amount: 594
  // },
  // {
  //   id: '4599',
  //   date: '2024-03-11T10:10:00',
  //   status: 'failed',
  //   email: 'mia.white@example.com',
  //   amount: 276
  // },
  // {
  //   id: '4598',
  //   date: '2024-03-11T08:50:00',
  //   status: 'refunded',
  //   email: 'william.brown@example.com',
  //   amount: 315
  // },
  // {
  //   id: '4597',
  //   date: '2024-03-10T19:45:00',
  //   status: 'paid',
  //   email: 'emma.davis@example.com',
  //   amount: 529
  // },
  // {
  //   id: '4596',
  //   date: '2024-03-10T15:55:00',
  //   status: 'paid',
  //   email: 'ethan.harris@example.com',
  //   amount: 639
  // }
])


</script>

<template>
		<div>
		<UButton @click="downloadBlob(docxBlob, 'Order.docx')" label="Скачать документ" />
	</div>

		<div class="font-serif text-l text-justify text-pretty w-full">
	<h1 class="font-bold">Заказ на поставку {{ orderData.orderNumber }} от {{ orderData.orderDate }}</h1>

	<table>
		<tr>
			<td>Поставщик:   </td>
			<td>
				<input placeholder="ИНН" v-model.trim.lazy="orderData.innSaller"/><br/>  
				<input placeholder="Название компании" v-model.lazy="orderData.companyNameSaller"/><br/> 
				<input placeholder="Юр.Адресс" v-model.lazy="orderData.urAdressSaller"/><br/> 
				<input placeholder="Контактный телефон" v-model.trim.lazy="orderData.mobileNumberSaller"/>
			</td>
		</tr>
		<tr>
			<td> 
				Покупатель: 
			</td>
			<td>
				<input placeholder="Название компании" v-model.lazy="orderData.companyNameBuyer"/><br/>
				<input placeholder="Юр.Адресс" v-model.lazy="orderData.urAdressBuyer"/><br/>
				<input placeholder="Контактный телефон" v-model.lazy="orderData.mobileNumberBuyer"/><br/>
			</td>
		</tr>
	</table>

	<UTable :columns="columns" :data="orderData.products" />

	<p>Всего наименований:{{ orderData.products.length }}, на сумму: {{ orderData.amount }} p.</p><br/>
	<p>Менеджер <input placeholder="Имя продавца" v-model.lazy="orderData.sallerName"/>               Покупатель {{ orderData.buyerName }}</p><br/>
	<textarea placeholder="Комментарии" v-model.lazy="orderData.comments" class="w-full max-h-50"/>
	</div>
</template>

<style lang="css" scoped>
* {
	line-height:1.2em;
}

h1,h2 {
	text-align: center;
	line-height: 3em;
}

p {
	text-indent: 0em;
	line-height: 1.5em;
}
</style>