<script setup lang="ts">
import type { OrderData, ProductsInOrder } from '~/types/contracts';
import { usePurchasesStore } from '~/stores/purchases';
import type { Product, Person } from '~/types/dealState';

const purchasesStore = usePurchasesStore()
const { purchases } = storeToRefs(purchasesStore)

const products: ProductsInOrder[] | any = purchases.value.goodsDeals?.[0]?.goods.goodsList?.map(product => ({
	name: product.name,
	article: product.article,
	quantity: product.quantity,
	units: product.units,
	price: product.price,
	amount: product.amount,
	type: product.type,
}))

const saller: Person = Object.assign({}, purchases.value.goodsDeals?.[0]?.saller)
const buyer: Person = Object.assign({}, purchases.value.goodsDeals?.[0]?.buyer)

const orderData: Ref<OrderData> = ref({
	orderNumber: Number(purchases.value.goodsDeals?.[0]?.dealNumber),
	orderDate: purchases.value.goodsDeals?.[0]?.date,
	comments: purchases.value.goodsDeals?.[0]?.goods.comments,
	amount: computed(() => purchases.value.goodsDeals?.[0]?.goods.amountPrice),
	amountWord: computed(() => purchases.value.goodsDeals?.[0]?.goods.amountWord),
	saller,
	buyer,
	products,
})

watch(() => orderData.value,
	async () => {
		purchasesStore.editGood(orderData.value.orderNumber, products)
		purchasesStore.editSallerGoodsDeal(orderData.value.orderNumber, saller)
		purchasesStore.editBuyerGoodsDeal(orderData.value.orderNumber, buyer)
		if (orderData.value.comments) {
			purchasesStore.editComments(orderData.value.orderNumber, orderData.value.comments)
		}
	},
	{ deep: true, immediate: true }
)

const element: Ref<HTMLElement | null> = useState('htmlOrder', () => ref(null))

const addGood = () => {
	const product: Product = {
		name: '',
		article: Number(),
		quantity: Number(),
		units: '',
		price: Number(),
		amount: Number(),
		type: 'товар'
	}
	orderData.value.products.push(product)
	purchasesStore.addNewGood(orderData.value.orderNumber, product)
}

const disabledInput = inject('disabledInput', 'true')

</script>

<template>
	<div ref="element" class="font-serif text-l text-justify text-pretty w-full p-5">
		<table>
			<tr>
				<td><span>Поставщик:</span> </td>
				<td style="padding-inline: 10px;">
					<input :disabled="disabledInput" class="" placeholder="ИНН" v-model.trim.lazy="orderData.saller.inn" /><br />
					<input :disabled="disabledInput" placeholder="Название компании"
						v-model.lazy="orderData.saller.companyName" /><br />
					<input :disabled="disabledInput" placeholder="Юр.Адресс" v-model.lazy="orderData.saller.legalAddress" /><br />
					<input :disabled="disabledInput" placeholder="Контактный телефон"
						v-model.trim.lazy="orderData.saller.mobileNumber" />
				</td>
			</tr>
			<tr>
				<td>
					<span>Покупатель:</span>
				</td>
				<td style="padding-inline: 10px;">
					<input :disabled="disabledInput" placeholder="Название компании"
						v-model.lazy="orderData.buyer.companyName" /><br />
					<input :disabled="disabledInput" placeholder="Юр.Адресс" v-model.lazy="orderData.buyer.legalAddress" /><br />
					<input :disabled="disabledInput" placeholder="Контактный телефон"
						v-model.lazy="orderData.buyer.mobileNumber" /><br />
				</td>
			</tr>
		</table>

		<h1 style="font-weight: 700;" class="font-bold my-2">Заказ на поставку {{ orderData.orderNumber }} от {{
			orderData.orderDate }}</h1>

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
						<input :disabled="disabledInput" class="w-75" placeholder="Название" v-model.lazy="product.name" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-20 text-center" placeholder="Артикул"
							v-model.lazy="product.article" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-13 text-center" placeholder="Кол-во"
							v-model.lazy="product.quantity" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-13 text-center" placeholder="Ед. изм."
							v-model.lazy="product.units" />
					</td>
					<td class="border">
						<input :disabled="disabledInput" class="w-20 text-center" placeholder="Цена" v-model.lazy="product.price" />
					</td>
					<td class="border">
						<span>{{ product.amount }}</span>
					</td>
				</tr>
				<tr :hidden="disabledInput">
					<td @click="addGood()" colspan="7" class="text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>
			</tbody>
		</table>

		<p><span>Всего наименований:{{ orderData.products.length }}, на сумму: {{ orderData.amount }} p.</span></p>
		<p><span class="underline underline-offset-4">{{ orderData.amountWord }}</span></p>
		<br />
		<p>
			<span style="text-align: start;">Менеджер </span>
			<input :disabled="disabledInput" placeholder="Имя продавца" v-model.lazy="orderData.saller.name" />
			<span style="text-align: center;">Покупатель</span>
			<input :disabled="disabledInput" placeholder="Имя покупателя" v-model.lazy="orderData.buyer.name" />
		</p>
		<br />

		<textarea :disabled="disabledInput" ref="comment" placeholder="Комментарии" v-model.lazy="orderData.comments"
			class="w-full max-h-20" />
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