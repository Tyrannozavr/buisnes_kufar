<script setup lang="ts">
import type { OrderData } from '~/types/contracts';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import type { Product, Person, GoodsDeal, ServicesDeal } from '~/types/dealState';
import { injectionKeys, RequestedType } from '~/constants/keys';

const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()

let products: Product[] = []
let saller = {} as Person
let buyer = {} as Person

const orderData: Ref<OrderData> = ref({
	orderNumber: NaN,
	orderDate: '',
	comments: '',
	amount: 0,
	amountWord: '',
	saller,
	buyer,
	products,
})

const insertState = inject(injectionKeys.insertStateKey, ref({
	purchasesStateGood: false,
	purchasesStateService: false,
	salesStateGood: false,
	salesStateService: false,
}))

let requestedData = ''

watch(() => insertState.value,
	() => {
		let lastGoodsDeal: GoodsDeal | undefined = undefined
		let lastServicesDeal: ServicesDeal | undefined = undefined

		if (insertState.value.purchasesStateGood) {
			requestedData = RequestedType.PURCHASES_GOOD
			if (purchasesStore.lastGoodsDeal) {
				lastGoodsDeal = purchasesStore.lastGoodsDeal
			}
			insertState.value.purchasesStateGood = false

		} else if (insertState.value.purchasesStateService) {
			requestedData = RequestedType.PURCHASES_SERVICE
			if (purchasesStore.lastServicesDeal) {
				lastServicesDeal = purchasesStore.lastServicesDeal
			}
			insertState.value.purchasesStateService = false

		} else if (insertState.value.salesStateGood) {
			requestedData = RequestedType.SALES_GOOD
			if (salesStore.lastGoodsDeal) {
				lastGoodsDeal = salesStore.lastGoodsDeal
			}
			insertState.value.salesStateGood = false

		} else if (insertState.value.salesStateService) {
			requestedData = RequestedType.SALES_SERVICE
			if (salesStore.lastServicesDeal) {
				lastServicesDeal = salesStore.lastServicesDeal
			}
			insertState.value.salesStateService = false
		}

		if ((requestedData === RequestedType.PURCHASES_GOOD || requestedData === RequestedType.SALES_GOOD) 
		&& lastGoodsDeal) {
			
			products = lastGoodsDeal.goods.goodsList?.map((product: Product) => ({
				name: product.name,
				article: product.article,
				quantity: product.quantity,
				units: product.units,
				price: product.price,
				amount: product.amount,
				type: product.type,
			}))

			saller = Object.assign({}, lastGoodsDeal?.saller)
			buyer = Object.assign({}, lastGoodsDeal?.buyer)

			orderData.value = {
				orderNumber: Number(lastGoodsDeal?.dealNumber),
				orderDate: lastGoodsDeal?.date,
				comments: lastGoodsDeal?.goods.comments,
				amount: lastGoodsDeal?.goods.amountPrice,
				amountWord: lastGoodsDeal?.goods.amountWord,
				saller,
				buyer,
				products,
			}
		}

		if ((requestedData === RequestedType.PURCHASES_SERVICE || requestedData === RequestedType.SALES_SERVICE) 
		&& lastServicesDeal) {
			
			products = lastServicesDeal.services.servicesList?.map((product: Product) => ({
				name: product.name,
				article: product.article,
				quantity: product.quantity,
				units: product.units,
				price: product.price,
				amount: product.amount,
				type: product.type,
			}))

			saller = Object.assign({}, lastServicesDeal?.saller)
			buyer = Object.assign({}, lastServicesDeal?.buyer)

			orderData.value = {
				orderNumber: Number(lastServicesDeal?.dealNumber),
				orderDate: lastServicesDeal?.date,
				comments: lastServicesDeal?.services.comments,
				amount: lastServicesDeal?.services.amountPrice,
				amountWord: lastServicesDeal?.services.amountWord,
				saller,
				buyer,
				products,
			}
		}
	},
	{ deep: true }
)

const changeState = inject(injectionKeys.changeStateOrderKey, ref(false))

watch(() => changeState.value,
	() => {
		if (requestedData === RequestedType.PURCHASES_GOOD) {
			purchasesStore.editGood(orderData.value.orderNumber, products)
			purchasesStore.editSallerGoodsDeal(orderData.value.orderNumber, saller)
			purchasesStore.editBuyerGoodsDeal(orderData.value.orderNumber, buyer)

			if (orderData.value.comments) {
				purchasesStore.editGoodsComments(orderData.value.orderNumber, orderData.value.comments)
			}

			setTimeout(() => {
				orderData.value.amount = purchasesStore?.lastGoodsDeal?.goods.amountPrice
				orderData.value.amountWord = purchasesStore?.lastGoodsDeal?.goods.amountWord
			}, 1)
			
		} else if (requestedData === RequestedType.PURCHASES_SERVICE) {
			purchasesStore.editService(orderData.value.orderNumber, products)
			purchasesStore.editSallerServicesDeal(orderData.value.orderNumber, saller)
			purchasesStore.editBuyerServicesDeal(orderData.value.orderNumber, buyer)

			if (orderData.value.comments) {
				purchasesStore.editServicesComments(orderData.value.orderNumber, orderData.value.comments)
			}

			setTimeout(() => {
				orderData.value.amount = purchasesStore?.lastServicesDeal?.services.amountPrice
				orderData.value.amountWord = purchasesStore?.lastServicesDeal?.services.amountWord
			}, 1)

		} else if (requestedData === RequestedType.SALES_GOOD) {
			salesStore.editGood(orderData.value.orderNumber, products)
			salesStore.editSallerGoodsDeal(orderData.value.orderNumber, saller)
			salesStore.editBuyerGoodsDeal(orderData.value.orderNumber, buyer)

			if (orderData.value.comments) {
				salesStore.editServicesComments(orderData.value.orderNumber, orderData.value.comments)
			}

			setTimeout(() => {
				orderData.value.amount = salesStore?.lastGoodsDeal?.goods.amountPrice
				orderData.value.amountWord = salesStore?.lastGoodsDeal?.goods.amountWord
			}, 1)

		} else if (requestedData === RequestedType.SALES_SERVICE) {
			salesStore.editService(orderData.value.orderNumber, products)
			salesStore.editSallerServicesDeal(orderData.value.orderNumber, saller)
			salesStore.editBuyerServicesDeal(orderData.value.orderNumber, buyer)

			if (orderData.value.comments) {
				salesStore.editServicesComments(orderData.value.orderNumber, orderData.value.comments)
			}

			setTimeout(() => {
				orderData.value.amount = salesStore?.lastServicesDeal?.services.amountPrice
				orderData.value.amountWord = salesStore?.lastServicesDeal?.services.amountWord
			}, 1)
		}
	},
	{ deep: true }
)

const element: Ref<HTMLElement | null> = useState('htmlOrder', () => ref(null))

const addProduct = () => {
	const productType: string = 
	(requestedData === RequestedType.PURCHASES_GOOD || requestedData === RequestedType.SALES_GOOD) 
	? 'товар' 
	: 'услуга'

	const product: Product = {
		name: '',
		article: Number(),
		quantity: Number(),
		units: '',
		price: Number(),
		amount: Number(),
		type: productType
	}

	orderData.value.products.push(product)
}

const isDisabled = inject(injectionKeys.isDisabledKey, ref(true)) 


//clear form button
const clearState = inject(injectionKeys.clearStateKey, ref(false))

const clearForm = () => {
	products = []
	saller = {} as Person
	buyer = {} as Person

	orderData.value = {
		orderNumber: NaN,
		orderDate: '',
		comments: '',
		amount: 0,
		amountWord: '',
		saller,
		buyer,
		products,
	}

}

watch(() => clearState.value,
	() => {
		if (clearState.value) {
			clearForm()
		}
	},
	{ deep: true }
)

//delete deal button
const removeDealState = inject(injectionKeys.removeDealStateKey, ref(false))

const removeDeal = (requestedData: string) => {
	if (requestedData === RequestedType.PURCHASES_GOOD) {
		purchasesStore.removeGoodsDeal(orderData.value.orderNumber)

	} else if (requestedData === RequestedType.PURCHASES_SERVICE) {
		purchasesStore.removeServicesDeal(orderData.value.orderNumber)

	} else if (requestedData === RequestedType.SALES_GOOD) {
		salesStore.removeGoodsDeal(orderData.value.orderNumber)

	} else if (requestedData === RequestedType.SALES_SERVICE) {
		salesStore.removeServicesDeal(orderData.value.orderNumber)
	}

	clearForm()
}

watch(() => removeDealState.value,
	() => {
		removeDeal(requestedData)
	},
	{ deep: true }
)

//remove product
const removeProduct = (product: any): void => {
	const index = orderData.value.products.indexOf(product)
	orderData.value.products.splice(index, 1)
}
</script>

<template>
	<div class="shadow-md m-1 bg-gray-50 overflow-y-hidden">
	<div ref="element" class="font-serif text-md text-justify text-pretty p-5 mt-3 h-[99%] overflow-y-hidden">
		<table>
			<tr>
				<td><span>Поставщик:</span> </td>
				<td style="padding-inline: 10px;">
					<input :disabled="isDisabled" class="" placeholder="ИНН" v-model.trim.lazy="orderData.saller.inn" /><br />
					<input :disabled="isDisabled" placeholder="Название компании"
						v-model.lazy="orderData.saller.companyName" /><br />
					<input :disabled="isDisabled" placeholder="Юр.Адресс" v-model.lazy="orderData.saller.legalAddress" /><br />
					<input :disabled="isDisabled" placeholder="Контактный телефон"
						v-model.trim.lazy="orderData.saller.mobileNumber" />
				</td>
			</tr>
			<tr>
				<td>
					<span>Покупатель:</span>
				</td>
				<td style="padding-inline: 10px;">
					<input :disabled="isDisabled" placeholder="Название компании"
						v-model.lazy="orderData.buyer.companyName" /><br />
					<input :disabled="isDisabled" placeholder="Юр.Адресс" v-model.lazy="orderData.buyer.legalAddress" /><br />
					<input :disabled="isDisabled" placeholder="Контактный телефон"
						v-model.lazy="orderData.buyer.mobileNumber" /><br />
				</td>
			</tr>
		</table>

		<h1 style="font-weight: 700;" class="font-bold my-2">Заказ на поставку 
			<span v-if="orderData.orderNumber">{{ orderData.orderNumber }}</span>
			 от {{ orderData.orderDate }}</h1>

		<table class="table-fixed p-5 mb-5 w-[99%] text-center" id="products">
			<thead>
				<th class="w-5 border"><span>№</span></th>
				<th class="w-50 border"><span>Название продукта</span></th>
				<th class="w-15 border"><span>Артикул</span></th>
				<th class="w-10 border"><span>Кол-во</span></th>
				<th class="w-13 border"><span>Ед. изм.</span></th>
				<th class="w-15 border"><span>Цена</span></th>
				<th class="w-20 border"><span>Сумма</span></th>
				<th class="w-1"><span></span></th>
			</thead>
			<tbody>
				<tr v-for="product in orderData.products">
					<td class="border">
						<span>{{ orderData.products.indexOf(product) + 1 }}</span>
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-72" placeholder="Название" v-model.lazy="product.name" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-21 text-center" placeholder="Артикул"
							v-model.lazy="product.article" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-14 text-center" placeholder="Кол-во"
							v-model.lazy="product.quantity" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-18 text-center" placeholder="Ед. изм."
							v-model.lazy="product.units" />
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-21 text-center" placeholder="Цена" v-model.lazy="product.price" />
					</td>
					<td class="border">
						<span class="">{{ product.amount }}</span>
					</td>
					<td>
						<span :hidden="isDisabled" class="w-[10px] cursor-pointer" @click="removeProduct(product)">
							<svg class="w-7 h-5 fill-none stroke-neutral-400 hover:stroke-red-400" xmlns="http://www.w3.org/2000/svg"
								width="32" height="32" viewBox="0 0 24 24">
								<g class="fill-white stroke-neutral-400 hover:stroke-red-400" stroke-linecap="round"
									stroke-linejoin="round" stroke-width="3">
									<circle cx="12" cy="12" r="10" />
									<path d="m15 9l-6 6m0-6l6 6" />
								</g>
							</svg>
						</span>
					</td>

				</tr>
				<tr :hidden="isDisabled">
					<td @click="addProduct()" colspan="7"
						class="border text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>
			</tbody>
		</table>

		<p><span>Всего наименований:{{ orderData.products.length }}, на сумму: 
			<span v-if="orderData.amount">{{ orderData.amount }} </span>
			p.</span></p>
		<p><span class="underline underline-offset-4">{{ orderData.amountWord }}</span></p>
		<br />
		<p>
			<span style="text-align: start;">Менеджер </span>
			<input :disabled="isDisabled" placeholder="Имя продавца" v-model.lazy="orderData.saller.name" />
			<span style="text-align: center;">Покупатель</span>
			<input :disabled="isDisabled" placeholder="Имя покупателя" v-model.lazy="orderData.buyer.name" />
		</p>
		<br />

		<textarea :disabled="isDisabled" ref="comment" placeholder="Комментарии" v-model.lazy="orderData.comments"
			class="w-full h-15 max-h-40" />
	</div>
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