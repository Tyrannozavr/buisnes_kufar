<script setup lang="ts">
import type { OrderData, ProductsInOrder } from '~/types/contracts';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import type { Product, GoodsDeal, ServicesDeal } from '~/types/dealState';
import { Editor, RequestedType, TemplateElement } from '~/constants/keys';
import { useInsertState } from '~/composables/useStates';
import { normalizeDate } from '~/utils/normalize';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import { useUserStore } from '~/stores/user';

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const { statePurchasesGood, statePurchasesService, stateSalesGood, stateSalesService } = useInsertState()

let products: ProductsInOrder[] = []
let saller: OrderData['saller'] = {}
let buyer: OrderData['buyer'] = {}

const orderData: Ref<OrderData> = ref({
  orderNumber: '',
  dealId: 0,
	orderDate: '',
	comments: '',
	amount: 0,
	amountWord: '',
	saller,
	buyer,
	products,
})

const insertState = useTypedState(Editor.INSERT_STATE)
let requestedData = ''
let goodsDeal: GoodsDeal | undefined = undefined
let servicesDeal: ServicesDeal | undefined = undefined

const fillQuery = () => {
  const query: Record<string, any> = {...route.query}

  if (orderData.value.dealId) {
    query.dealId = String(orderData.value.dealId)
  }

  if (userStore.companyId === orderData.value.buyer.companyId) {
    query.role = 'buyer'
  } else {
    query.role = 'seller'
  }

  if (orderData.value.products?.[0]?.type === 'Товар') {
    query.productType = 'goods'
  } else if (orderData.value.products?.[0]?.type === 'Услуга') {
    query.productType = 'services'
  }

  
  router.replace({
    query,
    hash: '#order'
  })
} 

const fillOrderData = () => {
  if ((requestedData === RequestedType.PURCHASES_GOOD || requestedData === RequestedType.SALES_GOOD)
    && goodsDeal) {

    products = goodsDeal.goods.goodsList?.map((product: Product): ProductsInOrder => ({
      name: product.name,
      article: product.article,
      quantity: product.quantity,
      units: product.units,
      price: product.price,
      amount: product.amount,
      type: product.type,
    })) || []

    saller = {
      companyId: goodsDeal?.saller.companyId,
      sallerName: goodsDeal?.saller.sallerName,
      companyName: goodsDeal?.saller.companyName,
      mobileNumber: goodsDeal?.saller.phone,
      legalAddress: goodsDeal?.saller.legalAddress,
      inn: Number(goodsDeal?.saller.inn) || 0,
    }
    buyer = {
      companyId: goodsDeal?.buyer.companyId,
      buyerName: goodsDeal?.buyer.buyerName,
      companyName: goodsDeal?.buyer.companyName,
      mobileNumber: goodsDeal?.buyer.phone,
      legalAddress: goodsDeal?.buyer.legalAddress,
      inn: Number(goodsDeal?.buyer.inn) || 0,
    }

    orderData.value = {
      orderNumber: goodsDeal?.buyerOrderNumber || '',
      dealId: goodsDeal?.dealId,
      orderDate: goodsDeal?.date,
      comments: goodsDeal?.goods.comments,
      amount: goodsDeal?.goods.amountPrice,
      amountWord: goodsDeal?.goods.amountWord,
      saller,
      buyer,
      products,
    }

    if (requestedData === RequestedType.SALES_GOOD) {
      orderData.value.orderNumber = goodsDeal?.sellerOrderNumber || ''
    }
  }

  if ((requestedData === RequestedType.PURCHASES_SERVICE || requestedData === RequestedType.SALES_SERVICE)
    && servicesDeal) {

    products = servicesDeal.services.servicesList?.map((product: Product): ProductsInOrder => ({
      name: product.name,
      article: product.article,
      quantity: product.quantity,
      units: product.units,
      price: product.price,
      amount: product.amount,
      type: product.type,
    })) || []

    saller = {
      companyId: servicesDeal?.saller.companyId,
      sallerName: servicesDeal?.saller.sallerName,
      companyName: servicesDeal?.saller.companyName,
      mobileNumber: servicesDeal?.saller.phone,
      legalAddress: servicesDeal?.saller.legalAddress,
      inn: Number(servicesDeal?.saller.inn) || 0,
    }
    buyer = {
      companyId: servicesDeal?.buyer.companyId,
      buyerName: servicesDeal?.buyer.buyerName,
      companyName: servicesDeal?.buyer.companyName,
      mobileNumber: servicesDeal?.buyer.phone,
      legalAddress: servicesDeal?.buyer.legalAddress,
      inn: Number(servicesDeal?.buyer.inn) || 0,
    }

    orderData.value = {
      orderNumber: servicesDeal?.buyerOrderNumber || '',
      dealId: servicesDeal?.dealId,
      orderDate: servicesDeal?.date,
      comments: servicesDeal?.services.comments,
      amount: servicesDeal?.services.amountPrice,
      amountWord: servicesDeal?.services.amountWord,
      saller,
      buyer,
      products,
    }

    if (requestedData === RequestedType.SALES_SERVICE) {
      orderData.value.orderNumber = servicesDeal?.sellerOrderNumber || ''
    }
  }

  fillQuery()
}

const fillFromQuery = () => {
  const query = route.query
  
  if (!query?.dealId || !query?.role || !query?.productType) return

  if (query.role === 'buyer') {
    if (query.productType === 'goods') {
      requestedData = RequestedType.PURCHASES_GOOD
      goodsDeal = purchasesStore.findGoodsDeal(Number(query.dealId))
    } else if (query.productType === 'services') {
      requestedData = RequestedType.PURCHASES_SERVICE
      servicesDeal = purchasesStore.findServicesDeal(Number(query.dealId))
    }
  } else if (query.role === 'seller') {
    if (query.productType === 'goods') {
      requestedData = RequestedType.SALES_GOOD
      goodsDeal = salesStore.findGoodsDeal(Number(query.dealId))
    } else if (query.productType === 'services') {
      requestedData = RequestedType.SALES_SERVICE
      servicesDeal = salesStore.findServicesDeal(Number(query.dealId))
    }
  }
  fillOrderData()
}

//заполнение формы при наличии данных в query или store
watch(
  () => [
    route.query.dealId,
    route.query.role,
    route.query.productType,
    route.query.dealId,
    route.hash,
    salesStore.sales?.goodsDeals?.length ?? 0,
    salesStore.sales?.servicesDeals?.length ?? 0,
    purchasesStore.purchases?.goodsDeals?.length ?? 0,
    purchasesStore.purchases?.servicesDeals?.length ?? 0,
  ],
  () => fillFromQuery(),
  { immediate: true, deep: true }
)

//присвоение конкретного состояния и значений,в зависимости от состояния
watch(() => insertState.value,
	() => {
		if (insertState.value.purchasesGood) {
			requestedData = RequestedType.PURCHASES_GOOD
			if (purchasesStore.lastGoodsDeal) {
				goodsDeal = purchasesStore.lastGoodsDeal
			}
			statePurchasesGood(false)

		} else if (insertState.value.purchasesService) {
			requestedData = RequestedType.PURCHASES_SERVICE
			if (purchasesStore.lastServicesDeal) {
				servicesDeal = purchasesStore.lastServicesDeal
			}
			statePurchasesService(false)

		} else if (insertState.value.salesGood) {
			requestedData = RequestedType.SALES_GOOD
			if (salesStore.lastGoodsDeal) {
				goodsDeal = salesStore.lastGoodsDeal
			}
			stateSalesGood(false)

		} else if (insertState.value.salesService) {
			requestedData = RequestedType.SALES_SERVICE
			if (salesStore.lastServicesDeal) {
				servicesDeal = salesStore.lastServicesDeal
			}
			stateSalesService(false)
    }
    fillOrderData()
	},
	{ deep: true }
)

const saveState = useTypedState(Editor.SAVE_STATE_ORDER)

watch(() => saveState.value,
	async () => {
		if (requestedData === RequestedType.PURCHASES_GOOD) {
			await purchasesStore.fullUpdateGoodsDeal(
				orderData.value.dealId,
				orderData.value.saller,
				orderData.value.buyer,
				orderData.value.products,
				orderData.value.comments)

      orderData.value.amount = purchasesStore?.lastGoodsDeal?.goods.amountPrice
      orderData.value.amountWord = purchasesStore?.lastGoodsDeal?.goods.amountWord

		} else if (requestedData === RequestedType.PURCHASES_SERVICE) {
			await purchasesStore.fullUpdateServicesDeal(
				orderData.value.dealId,
				orderData.value.saller,
				orderData.value.buyer,
				orderData.value.products,
				orderData.value.comments)

      orderData.value.amount = purchasesStore?.lastServicesDeal?.services.amountPrice
      orderData.value.amountWord = purchasesStore?.lastServicesDeal?.services.amountWord

		} else if (requestedData === RequestedType.SALES_GOOD) {
			await salesStore.fullUpdateGoodsDeal(
				orderData.value.dealId,
				orderData.value.saller,
				orderData.value.buyer,
				orderData.value.products,
				orderData.value.comments)

      orderData.value.amount = salesStore?.lastGoodsDeal?.goods.amountPrice
      orderData.value.amountWord = salesStore?.lastGoodsDeal?.goods.amountWord

		} else if (requestedData === RequestedType.SALES_SERVICE) {
			await salesStore.fullUpdateServicesDeal(
				orderData.value.dealId,
				orderData.value.saller,
				orderData.value.buyer,
				orderData.value.products,
				orderData.value.comments)

      orderData.value.amount = salesStore?.lastServicesDeal?.services.amountPrice
      orderData.value.amountWord = salesStore?.lastServicesDeal?.services.amountWord
		}
	},
	{ deep: true }
)

const addProduct = () => {
	// По умолчанию считаем "товар", а "услуга" — только если явно выбран тип сделки услуг.
	const productType: string =
		(requestedData === RequestedType.PURCHASES_SERVICE || requestedData === RequestedType.SALES_SERVICE)
			? 'Услуга'
			: 'Товар'

  const product: ProductsInOrder = {
		name: '',
    article: '',
    quantity: 0,
		units: '',
    price: 0,
    amount: 0,
		type: productType
	}

	orderData.value.products.push(product)
}

const isDisabled = useTypedState(Editor.IS_DISABLED)

//clear form button
const clearState = useTypedState(Editor.CLEAR_STATE)

const clearForm = () => {
	products = []
  saller = {}
  buyer = {}

	orderData.value = {
		orderNumber: '',
		dealId: 0,
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

//delete deal
const removeDealState = useTypedState(Editor.REMOVE_DEAL)

const removeDeal = (requestedData: string) => {
	if (requestedData === RequestedType.PURCHASES_GOOD) {
		purchasesStore.removeGoodsDeal(orderData.value.dealId)

	} else if (requestedData === RequestedType.PURCHASES_SERVICE) {
		purchasesStore.removeServicesDeal(orderData.value.dealId)

	} else if (requestedData === RequestedType.SALES_GOOD) {
		salesStore.removeGoodsDeal(orderData.value.dealId)

	} else if (requestedData === RequestedType.SALES_SERVICE) {
		salesStore.removeServicesDeal(orderData.value.dealId)
	}

	requestedData = ''
	goodsDeal = undefined
	servicesDeal = undefined
	clearForm()
}

watch(() => removeDealState.value,
	() => {
		if (removeDealState.value) {
			removeDeal(requestedData)
		}
	},
	{ deep: true }
)

//remove product
const removeProduct = (product: ProductsInOrder): void => {
	const index = orderData.value.products.indexOf(product)
	orderData.value.products.splice(index, 1)
}

const html = useTemplateRef('html')
const htmlOrder = useTypedState(TemplateElement.ORDER, () => ref(null))

onMounted(() => {
	htmlOrder.value = html.value
})
</script>

<template>
	<div ref="html">

		<table>
			<tbody>
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
			</tbody>
		</table>

		<h1 style="font-weight: 700;" class="font-bold my-2">Заказ на поставку
			<span>{{ orderData.orderNumber }}</span>
			от {{ normalizeDate(orderData.orderDate || '') }} г.
		</h1>

			<table class="table-fixed p-5 mb-5 w-[99%] text-center" id="products">
				<thead>
					<tr>
						<td class="w-5 border"><span>№</span></td>
						<td class="w-50 border"><span>Название продукта</span></td>
						<td class="w-15 border"><span>Артикул</span></td>
						<td class="w-10 border"><span>Кол-во</span></td>
						<td class="w-13 border"><span>Ед. изм.</span></td>
						<td class="w-15 border"><span>Цена</span></td>
						<td class="w-20 border"><span>Сумма</span></td>
						<td class="w-1"><span></span></td>
					</tr>
				</thead>
				<tbody>
					<tr v-for="product in orderData.products">
						<td class="border">
							<span>{{ orderData.products.indexOf(product) + 1 }}</span>
						</td>
						<td class="border">
							<input :disabled="isDisabled" class="w-72" placeholder="Название" v-model.trim="product.name" />
						</td>
						<td class="border">
							<input :disabled="isDisabled" class="w-21 text-center" placeholder="Артикул"
								v-model.number="product.article" />
						</td>
						<td class="border">
							<input :disabled="isDisabled" class="w-14 text-center" placeholder="Кол-во"
								v-model.number="product.quantity" />
						</td>
						<td class="border">
							<input :disabled="isDisabled" class="w-18 text-center" placeholder="Ед. изм."
								v-model.trim="product.units" />
						</td>
						<td class="border">
							<input :disabled="isDisabled" class="w-21 text-center" placeholder="Цена" v-model.number="product.price" />
						</td>
						<td class="border">
							<span class="">{{ product.amount }}</span>
						</td>
						<td>
							<span :hidden="isDisabled" class="w-[10px] cursor-pointer" @click="removeProduct(product)">
								<svg class="w-7 h-5 fill-none stroke-neutral-400 hover:stroke-red-400"
									xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
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
						<td colspan="7" class="border text-left">
							<button
								type="button"
								class="w-full text-left text-gray-400 hover:text-gray-700 cursor-pointer"
								@click="addProduct()"
							>
								Добавить товар
							</button>
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
			<input :disabled="isDisabled" placeholder="Имя продавца" v-model.lazy="orderData.saller.sallerName" />
			<span style="text-align: center;">Покупатель</span>
			<input :disabled="isDisabled" placeholder="Имя покупателя" v-model.lazy="orderData.buyer.buyerName" />
		</p>
		<br />

			<textarea :disabled="isDisabled" ref="comment" placeholder="Комментарии" v-model.lazy="orderData.comments"
				class="w-full h-15 max-h-40" />
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