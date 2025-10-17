<script setup lang="ts">
import type { OrderData, ProductsInOrder } from '~/types/contracts';
import { usePurchasesStore } from '~/stores/purchases';
import type { Product, Person, GoodsDeal, ServicesDeal } from '~/types/dealState';
import type { Insert } from '~/types/contracts';


const purchasesStore = usePurchasesStore()
const { purchases } = storeToRefs(purchasesStore)

let products: Product[] = []
let saller: Person = {
	inn: 0,
	name: "",
	companyName: "",
	legalAddress: "",
	mobileNumber: "",
}
let buyer: Person = {
	inn: 0,
	name: "",
	companyName: "",
	legalAddress: "",
	mobileNumber: "",
}

let amount: ComputedRef<number> = computed(() => NaN)
let amountWord: ComputedRef<string> = computed(() => '')

let orderData: Ref<OrderData> = ref({
	orderNumber: NaN,
	orderDate: '',
	comments: '',
	amount: amount.value,
	amountWord: amountWord.value,
	saller,
	buyer,
	products,
})

const insertState = inject<Ref<Insert>>('insertState', ref({
	purchasesStateGood: false,
	purchasesStateService: false,
	salesStateGood: false,
	salesStateService: false,
}))

let requestedData: string = ''


watch(() => insertState.value,
	() => {
		let lastGoodsDeal: GoodsDeal | undefined = undefined
		let lastServicesDeal: ServicesDeal | undefined = undefined

		if (insertState.value.purchasesStateGood) {
			requestedData = 'purchases-good'
			if (purchasesStore.lastGoodsDeal) {
				lastGoodsDeal = purchasesStore.lastGoodsDeal
			}
			insertState.value.purchasesStateGood = false

		} else if (insertState.value.purchasesStateService) {
			requestedData = 'purchases-service'
			if (purchasesStore.lastServiceDeal) {
				lastServicesDeal = purchasesStore.lastServiceDeal
			}
			insertState.value.purchasesStateService = false

		} else if (insertState.value.salesStateGood) {
			requestedData = 'sales-good'
			insertState.value.salesStateGood = false

		} else if (insertState.value.salesStateService) {
			requestedData = 'sales-service'
			insertState.value.salesStateService = false
		}

		console.log(requestedData)

		if ((requestedData === 'purchases-good' || 'sales-good') && typeof (lastGoodsDeal) !== 'undefined') {
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

			amount = computed(() => lastGoodsDeal?.goods.amountPrice)
			amountWord = computed(() => lastGoodsDeal?.goods.amountWord)

			orderData.value = {
				orderNumber: Number(lastGoodsDeal?.dealNumber),
				orderDate: lastGoodsDeal?.date,
				comments: lastGoodsDeal?.goods.comments,
				amount: amount.value,
				amountWord: amountWord.value,
				saller,
				buyer,
				products,
			}
		}

		if ((requestedData === 'purchases-service' || 'sales-service') && typeof (lastServicesDeal) !== 'undefined') {
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

			amount = computed(() => lastServicesDeal?.services.amountPrice)
			amountWord = computed(() => lastServicesDeal?.services.amountWord)

			orderData.value = {
				orderNumber: Number(lastServicesDeal?.dealNumber),
				orderDate: lastServicesDeal?.date,
				comments: lastServicesDeal?.services.comments,
				amount: amount.value,
				amountWord: amountWord.value,
				saller,
				buyer,
				products,
			}
		}
	},
	{ deep: true }
)

watch(() => orderData.value,
	() => {
		if (requestedData === 'purchases-good') {
			purchasesStore.editGood(orderData.value.orderNumber, products)
			purchasesStore.editSallerGoodsDeal(orderData.value.orderNumber, saller)
			purchasesStore.editBuyerGoodsDeal(orderData.value.orderNumber, buyer)

			if (orderData.value.comments) {
				purchasesStore.editGoodsComments(orderData.value.orderNumber, orderData.value.comments)
			}
		} else if (requestedData === 'purchases-service') {
			purchasesStore.editService(orderData.value.orderNumber, products)
			purchasesStore.editSallerServicesDeal(orderData.value.orderNumber, saller)
			purchasesStore.editBuyerServicesDeal(orderData.value.orderNumber, buyer)

			if (orderData.value.comments) {
				purchasesStore.editServicesComments(orderData.value.orderNumber, orderData.value.comments)
			}
		}

		orderData.value.amount = amount.value
		orderData.value.amountWord = amountWord.value

		console.log(orderData.value)
	},
	{ deep: true }
)

const element: Ref<HTMLElement | null> = useState('htmlOrder', () => ref(null))

const addProduct = () => {
	const productType: string = requestedData === 'purchases-good' || 'sales-good' ? 'товар' : 'услуга'
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

	if (requestedData === 'purchases-good') {
		purchasesStore.addNewGood(orderData.value.orderNumber, product)
	} else if (requestedData === 'purchases-service') {
		purchasesStore.addNewService(orderData.value.orderNumber, product)
	}

}

const disabledInput = inject<Ref<boolean>>('disabledInput', ref(true))

//clear form button
let clearState = inject<Ref<boolean>>('clearState', ref(false))

const clearForm = () => {
	console.log('clearForm')
	products = []
	saller = {
		inn: 0,
		name: "",
		companyName: "",
		legalAddress: "",
		mobileNumber: "",
	}
	buyer = {
		inn: 0,
		name: "",
		companyName: "",
		legalAddress: "",
		mobileNumber: "",
	}

	amount = computed(() => NaN)
	amountWord = computed(() => '')

	orderData.value = {
		orderNumber: NaN,
		orderDate: '',
		comments: '',
		amount: amount.value,
		amountWord: amountWord.value,
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
const removeDealState = inject<Ref<boolean>>('removeDealState', ref(false))

const removeDeal = (requestedData: string) => {
	if (requestedData === 'purchases-good') {
		purchasesStore.removeGoodsDeal(orderData.value.orderNumber)

	} else if (requestedData === 'purchases-service') {
		purchasesStore.removeServicesDeal(orderData.value.orderNumber)

	} else if (requestedData === 'sales-good') {
		//логика удаления из другого store

	} else if (requestedData === 'sales-service') {
		//логика удаления из другого store
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
	orderData.value.products.splice(index,1)
}
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

		<table class="table-fixed p-5 mb-5 w-[99%] text-center" id="products">
			<thead>
				<th class="w-7 border"><span>№</span></th>
				<th class="w-55 border"><span>Название продукта</span></th>
				<th class="w-15 border"><span>Артикул</span></th>
				<th class="w-10 border"><span>Кол-во</span></th>
				<th class="w-10 border"><span>Ед. изм.</span></th>
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
							<span class="">{{ product.amount }}</span>
						<!-- <UButton  color="neutral" variant="subtle" class=" hover:bg-red-400 rounded-full"/> -->
					</td>
					<td>
						<span :hidden="disabledInput" class="w-[10px] cursor-pointer" @click="removeProduct(product)">
								<svg class="w-7 h-5 fill-none stroke-neutral-400 hover:stroke-red-400" xmlns="http://www.w3.org/2000/svg" width="32" height="32"
									viewBox="0 0 24 24">
									<g class="fill-white stroke-neutral-400 hover:stroke-red-400" stroke-linecap="round" stroke-linejoin="round" stroke-width="3">
										<circle cx="12" cy="12" r="10" />
										<path d="m15 9l-6 6m0-6l6 6" />
									</g>
								</svg>
							</span>
					</td>
					
				</tr>
				<tr :hidden="disabledInput">
					<td @click="addProduct()" colspan="7" class="border text-left text-gray-400 hover:text-gray-700 cursor-pointer">
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