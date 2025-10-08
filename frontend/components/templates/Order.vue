<script setup lang="ts">
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import type { OrderData, ProductsInOrder } from '~/types/contracts';

const { generateDocxOrder } = useDocxGenerator()

const props = defineProps<{
	data: OrderData
}>()

const emit = defineEmits<{
	(e: 'inputData', orderData: OrderData): void,
	(e: 'orderHtml', element: HTMLElement | null): void
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

let docxBlob: Blob = await generateDocxOrder(orderData.value)

watch(() => orderData.value,
	async () => {
		docxBlob = await generateDocxOrder(orderData.value)

		orderData.value.products.map(product => {
			product.productAmount = product.price * product.quantity
		})
		orderData.value.amount = orderData.value.products.reduce((acc: number ,product: ProductsInOrder) => product.productAmount + acc, 0)

		emit('inputData', orderData.value)
		emit('orderHtml', element.value)
	},
	{ deep: true, immediate: true }
)

const element: Ref<HTMLElement | null> = ref(null)


const addProduct = () => {
	const product: ProductsInOrder = {
		name: '',
		article: Number(),
		quantity: Number(),
		units: '',
		price: Number(),
		productAmount: Number(),
	}
	orderData.value.products.push(product)
}

const disabledInput = inject('disabledInput', 'true')

</script>

<template>
	<div ref="element" class="font-serif text-l text-justify text-pretty w-full p-5">
		<table >
			<tr>
				<td><span>Поставщик:</span> </td>
				<td style="padding-inline: 10px;">
					<input :disabled="disabledInput" class="" placeholder="ИНН" v-model.trim.lazy="orderData.innSaller" /><br />
					<input :disabled="disabledInput" placeholder="Название компании" v-model.lazy="orderData.companyNameSaller" /><br />
					<input :disabled="disabledInput" placeholder="Юр.Адресс" v-model.lazy="orderData.urAdressSaller" /><br />
					<input :disabled="disabledInput" placeholder="Контактный телефон" v-model.trim.lazy="orderData.mobileNumberSaller" />
				</td>
			</tr>
			<tr>
				<td>
					<span>Покупатель:</span>
				</td>
				<td style="padding-inline: 10px;">
					<input :disabled="disabledInput" placeholder="Название компании" v-model.lazy="orderData.companyNameBuyer" /><br />
					<input :disabled="disabledInput" placeholder="Юр.Адресс" v-model.lazy="orderData.urAdressBuyer" /><br />
					<input :disabled="disabledInput" placeholder="Контактный телефон" v-model.lazy="orderData.mobileNumberBuyer" /><br />
				</td>
			</tr>
		</table>

		<h1 style="font-weight: 700;" class="font-bold my-2">Заказ на поставку {{ orderData.orderNumber }} от {{ orderData.orderDate }}</h1>

		<table class="table-fixed border p-5 mb-5 w-full text-center" id="products">
			<thead>
				<th class="w-7 border"><span>№</span></th>
				<th class="w-55 border"><span>Название продукта</span></th>
				<th class="w-15 border"><span>Артикул</span></th>
				<th class="w-10 border"><span>Кол-во</span></th>
				<th class="w-10 border"><span>Ед. изм.</span></th>
				<th class="w-15 border"><span>Цена</span></th>
				<th class="w-20 border"><span>Сумма</span></th>
			</thead>
			<tbody>
				<tr v-for="product in orderData.products">
					<td class="border">
						<span>{{ orderData.products.indexOf(product) + 1 }}</span>
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-75" placeholder="Название" v-model="product.name" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-20 text-center" placeholder="Артикул" v-model="product.article" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-13 text-center" placeholder="Кол-во" v-model="product.quantity" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-13 text-center" placeholder="Ед. изм." v-model="product.units" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-20 text-center" placeholder="Цена" v-model="product.price"/>
					</td>
					<td class="border">
						<span>{{ product.productAmount }}</span>
					</td>
				</tr>
				<tr :hidden="disabledInput">
					<td @click="addProduct()" colspan="7" class="text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>
			</tbody>
		</table>

		<p><span>Всего наименований:{{ orderData.products.length }}, на сумму: {{ orderData.amount }} p.</span></p>
		<br />
		<p>
			<span style="text-align: start;" >Менеджер </span>
			<input :disabled="disabledInput" placeholder="Имя продавца" v-model.lazy="orderData.sallerName" /> 
			<span style="text-align: center;">Покупатель</span>
			<input :disabled="disabledInput" placeholder="Имя покупателя" v-model.lazy="orderData.buyerName" />
		</p>
		<br />

		<textarea :disabled="disabledInput" ref="comment" placeholder="Комментарии" v-model.lazy="orderData.comments" class="w-full max-h-20" />
	</div>
</template>

<style lang="css" scoped>
* {
	line-height: 1.2em;
}

h1,
h2 {
	text-align: center;
	line-height: 3em;
}

p {
	text-indent: 0em;
	line-height: 1.5em;
}

input,
textarea {
	/* margin: 3px 0 3px 3px; */
	line-height: 1.75;
	padding: 1px 5px;
	vertical-align: middle;
}
</style>