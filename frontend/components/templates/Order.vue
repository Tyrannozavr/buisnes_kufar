<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui';
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import type { OrderData, ProductsInOrder } from '~/types/contracts';
import html2canvas from 'html2canvas-pro'
import jspdf, { jsPDF } from 'jspdf'

const { generateDocxOrder, downloadBlob } = useDocxGenerator()

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

		emit('inputData', orderData.value)
		emit('orderHtml', element.value)
	},
	{ deep: true, immediate: true }
)

const element: Ref<HTMLElement | null> = ref(null)


const addProduct = () => {
	const product: ProductsInOrder = {
		name: '',
		article: NaN,
		quantity: NaN,
		units: '',
		price: NaN,
		productAmount: NaN,
	}
	orderData.value.products.push(product)
}


// onMounted(() => {
// 	const replaceTextareasAndInputs = (element: any) => {
// 		const newElement: HTMLElement = element.cloneNode(true)
// 		const textareas = newElement.querySelectorAll('textarea')
// 		const inputs = newElement.querySelectorAll('input')

// 		textareas.forEach((textarea: any) => {
// 			const div = document.createElement('div')
// 			div.textContent = textarea.value
// 			div.style.cssText = getComputedStyle(textarea).cssText
// 			div.style.whiteSpace = 'pre-wrap'
// 			div.style.display = 'block'
// 			div.style.minHeight = textarea.offsetHeight + 'px'
// 			div.style.padding = '3px'
// 			textarea.parentNode?.replaceChild(div, textarea)
// 		});

// 		inputs.forEach((input: any) => {
// 			const span = document.createElement('span')
// 			span.textContent = input.value
// 			span.style.cssText = getComputedStyle(input).cssText
// 			span.style.display = 'inline'
// 			span.style.minHeight = input.offsetHeight + 'px'
// 			span.style.minWidth = input.offsetWidth + 'px'
// 			span.style.padding = '1px'
// 			input.parentNode?.replaceChild(span, input)
// 		})

// 		return newElement
// 	}
// 	const newElement = replaceTextareasAndInputs(element.value)
// 	console.log(newElement)
// })

</script>

<template>
	<div ref="element" class="font-serif text-l text-justify text-pretty w-full p-5">
		<table >
			<tr>
				<td>Поставщик: </td>
				<td style="padding-inline: 10px;">
					<input placeholder="ИНН" v-model.trim.lazy="orderData.innSaller" /><br />
					<input placeholder="Название компании" v-model.lazy="orderData.companyNameSaller" /><br />
					<input placeholder="Юр.Адресс" v-model.lazy="orderData.urAdressSaller" /><br />
					<input placeholder="Контактный телефон" v-model.trim.lazy="orderData.mobileNumberSaller" />
				</td>
			</tr>
			<tr>
				<td>
					Покупатель:
				</td>
				<td style="padding-inline: 10px;">
					<input placeholder="Название компании" v-model.lazy="orderData.companyNameBuyer" /><br />
					<input placeholder="Юр.Адресс" v-model.lazy="orderData.urAdressBuyer" /><br />
					<input placeholder="Контактный телефон" v-model.lazy="orderData.mobileNumberBuyer" /><br />
				</td>
			</tr>
		</table>

		<h1 style="font-weight: 700;" class="font-bold my-2">Заказ на поставку {{ orderData.orderNumber }} от {{ orderData.orderDate }}</h1>

		<table class="table-fixed border p-5 mb-5 w-full text-center" id="products">
			<thead>
				<th class="w-7 border">№</th>
				<th class="w-55 border">Название продукта</th>
				<th class="w-15 border">Артикул</th>
				<th class="w-10 border">Кол-во</th>
				<th class="w-10 border">Ед. изм.</th>
				<th class="w-15 border">Цена</th>
				<th class="w-20 border">Сумма</th>
			</thead>
			<tbody>
				<tr>
					<td class="border">
						0
					</td>
					<td class="border">
						<input class="w-65" placeholder="Название" value="falos" />
					</td>
					<td class="border">
						<input class="w-23 text-center" placeholder="Артикул" value="777" />
					</td>
					<td class="border">
						<input class="w-15 text-center" placeholder="Кол-во" value="10" />
					</td>
					<td class="border">
						<input class="w-13 text-center" placeholder="Ед. изм." value="шт" />
					</td>
					<td class="border">
						1000
					</td>
					<td class="border">
						100000
					</td>
				</tr>
				<tr v-for="product in orderData.products">
					<td class="border">
						{{ orderData.products.indexOf(product) + 1 }}
					</td>
					<td class="border">
						<input class="w-65" placeholder="Название" :value="product.name" />
					</td>
					<td class="border">
						<input class="w-23 text-center" placeholder="Артикул" :value="product.article" />
					</td>
					<td class="border">
						<input class="w-15 text-center" placeholder="Кол-во" :value="product.quantity" />
					</td>
					<td class="border">
						<input class="w-13 text-center" placeholder="Ед. изм." :value="product.units" />
					</td>
					<td class="border">
						{{ product.price }}
					</td>
					<td class="border">
						{{ product.productAmount }}
					</td>
				</tr>
				<tr hidden>
					<td @click="addProduct()" colspan="7" class="text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>
			</tbody>
		</table>

		<p>Всего наименований:{{ orderData.products.length }}, на сумму: {{ orderData.amount }} p.</p><br />
		<p><span style="text-align: left;" >Менеджер </span>
			<input placeholder="Имя продавца" v-model.lazy="orderData.sallerName" /> 
			<span style="text-align: center;">Покупатель </span>
			<input placeholder="Имя покупателя" v-model.lazy="orderData.buyerName" />
		</p>
		<br />

		<textarea ref="comment" placeholder="Комментарии" v-model.lazy="orderData.comments" class="w-full max-h-20" />
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