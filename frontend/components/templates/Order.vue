<script setup lang="ts">
import type { OrderData, ProductsInOrder } from '~/types/order';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import type { Product, GoodsDeal } from '~/types/dealState';
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
const { statePurchasesGood, stateSalesGood } = useInsertState()

const saveState = useTypedState(Editor.SAVE_STATE_ORDER)
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const clearState = useTypedState(Editor.CLEAR_STATE)
const removeDealState = useTypedState(Editor.REMOVE_DEAL)

const html = useTemplateRef('html')
const htmlOrder = useTypedState(TemplateElement.ORDER, () => ref(null))

const insertState = useTypedState(Editor.INSERT_STATE)
const goodsDeal: Ref<GoodsDeal | undefined> = ref(undefined)
let requestedData = ''

let products: ProductsInOrder[] = []
let seller: OrderData['seller'] = {}
let buyer: OrderData['buyer'] = {}

const orderData: Ref<OrderData> = ref({
  orderNumber: '',
  dealId: 0,
	orderDate: '',
	comments: '',
	amount: 0,
	amountWord: '',
	seller,
	buyer,
	products,
})

//заполнение query параметров по данным в форме
const fillQuery = () => {
  const query: Record<string, any> = {...route.query}

  if (orderData.value.dealId) {
    query.dealId = String(orderData.value.dealId)
  }

  if (userStore.companyId === orderData.value.buyer.companyId) {
    query.role = 'buyer'
  } else if (userStore.companyId === orderData.value.seller.companyId) {
    query.role = 'seller'
  }

  router.replace({
    query,
    hash: '#order'
  })
} 

//заполнение формы по данным сделки
const fillOrderData = () => {
  if ((requestedData === RequestedType.PURCHASES_GOOD || requestedData === RequestedType.SALES_GOOD)
    && goodsDeal.value) {

    products = (goodsDeal.value.goods.goodsList ?? []).map((product: Product): ProductsInOrder => ({
      name: product.name,
      article: product.article,
      quantity: product.quantity,
      units: product.units,
      price: product.price,
      amount: product.amount,
    }))
    seller = {
      companyId: goodsDeal.value.seller.companyId,
      sellerName: goodsDeal.value.seller.sellerName,
      companyName: goodsDeal.value.seller.companyName,
      mobileNumber: goodsDeal.value.seller.phone,
      legalAddress: goodsDeal.value.seller.legalAddress,
      inn: Number(goodsDeal.value.seller.inn) || 0,
    }
    buyer = {
      companyId: goodsDeal.value.buyer.companyId,
      buyerName: goodsDeal.value.buyer.buyerName,
      companyName: goodsDeal.value.buyer.companyName,
      mobileNumber: goodsDeal.value.buyer.phone,
      legalAddress: goodsDeal.value.buyer.legalAddress,
      inn: Number(goodsDeal.value.buyer.inn) || 0,
    }

    orderData.value = {
      orderNumber: requestedData === RequestedType.PURCHASES_GOOD ? goodsDeal.value.buyerOrderNumber || '' : goodsDeal.value.sellerOrderNumber || '',
      dealId: goodsDeal.value.dealId,
      orderDate: goodsDeal.value.date,
      comments: goodsDeal.value.goods.comments,
      amount: goodsDeal.value.goods.amountPrice,
      amountWord: goodsDeal.value.goods.amountWord,
      seller,
      buyer,
      products: [...products],
    }
  } 
  fillQuery()
}

//заполнение формы по данным сделки из query
const fillFromQuery = () => {
  const query = route.query
  if (!query?.dealId || !query?.role) return

  if (query.role === 'buyer') {
    requestedData = RequestedType.PURCHASES_GOOD
    goodsDeal.value = purchasesStore.findGoodsDeal(Number(query.dealId)) ?? undefined
  } else if (query.role === 'seller') {
    requestedData = RequestedType.SALES_GOOD
    goodsDeal.value = salesStore.findGoodsDeal(Number(query.dealId)) ?? undefined
  }
  fillOrderData()
}

//заполнение формы из query при наличии данных в store
watch(
  () => [
    route.query.dealId,
    salesStore.sales?.goodsDeals?.length ?? 0,
    purchasesStore.purchases?.goodsDeals?.length ?? 0,
  ],
  () => fillFromQuery(),
  { immediate: true, deep: true }
)

//присвоение конкретного состояния и значений,в зависимости от выбранного типа заполнения данных через меню
watch(() => insertState.value,
	() => {
    const toast = useToast()
    
		if (insertState.value.purchasesGood) {
			requestedData = RequestedType.PURCHASES_GOOD
			goodsDeal.value = purchasesStore.lastGoodsDeal ?? undefined
			statePurchasesGood(false)
			if (!goodsDeal.value) {
				toast.add({ title: 'Нет данных', description: 'Нет последней закупки по товарам. Сначала откройте заказ из раздела «Мои закупки».', color: 'warning' })
			}
		} else if (insertState.value.salesGood) {
			requestedData = RequestedType.SALES_GOOD
			goodsDeal.value = salesStore.lastGoodsDeal ?? undefined
			stateSalesGood(false)
			if (!goodsDeal.value) {
				toast.add({ title: 'Нет данных', description: 'Нет последней продажи по товарам. Сначала откройте заказ из раздела «Мои продажи».', color: 'warning' })
			}
		} 
		fillOrderData()
	},
	{ deep: true }
)

//сохранение заказа в store при нажатии на кнопку сохранения в меню
watch(() => saveState.value,
	async () => {
    if (!saveState.value) return
		const dealId = orderData.value.dealId

		if (requestedData === RequestedType.PURCHASES_GOOD) {
			await purchasesStore.fullUpdateGoodsDeal(
				dealId,
				orderData.value.seller,
				orderData.value.buyer,
				orderData.value.products,
				orderData.value.comments)
			orderData.value.amount = purchasesStore?.lastGoodsDeal?.goods.amountPrice
			orderData.value.amountWord = purchasesStore?.lastGoodsDeal?.goods.amountWord
		} else if (requestedData === RequestedType.SALES_GOOD) {
			await salesStore.fullUpdateGoodsDeal(
				dealId,
				orderData.value.seller,
				orderData.value.buyer,
				orderData.value.products,
				orderData.value.comments)
			orderData.value.amount = salesStore?.lastGoodsDeal?.goods.amountPrice
			orderData.value.amountWord = salesStore?.lastGoodsDeal?.goods.amountWord
		}
	},
	{ deep: true }
)

//добавление товара в заказ в компоненте
const addProduct = () => {
  const product: ProductsInOrder = {
		name: '',
    article: '',
    quantity: 0,
		units: '',
    price: 0,
    amount: 0,
	}

	orderData.value.products.push(product)
}

//очистка формы
const clearForm = () => {
	products = []
  seller = {}
  buyer = {}

	orderData.value = {
		orderNumber: '',
		dealId: 0,
		orderDate: '',
		comments: '',
		amount: 0,
		amountWord: '',
		seller,
		buyer,
		products,
	}
}

//очистка формы при нажатии на кнопку очистки в меню
watch(() => clearState.value,
	() => {
		if (clearState.value) {
			clearForm()
		}
	},
	{ deep: true }
)

//удаление сделки из store
const removeDeal = (requestedData: string) => {
	if (requestedData === RequestedType.PURCHASES_GOOD) {
    purchasesStore.removeGoodsDeal(orderData.value.dealId)
	} else if (requestedData === RequestedType.SALES_GOOD) {
		salesStore.removeGoodsDeal(orderData.value.dealId)
	} 

	requestedData = ''
	goodsDeal.value = undefined
	clearForm()
}

//удаление сделки из store при нажатии на кнопку удаления в меню
watch(() => removeDealState.value,
	() => {
		if (removeDealState.value) {
			removeDeal(requestedData)
		}
	},
	{ deep: true }
)

//удаление товара из заказа в компоненте
const removeProduct = (product: ProductsInOrder): void => {
	const index = orderData.value.products.indexOf(product)
	orderData.value.products.splice(index, 1)
}

//заполнение htmlOrder
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
						<input :disabled="isDisabled" class="" placeholder="ИНН" v-model.trim.lazy="orderData.seller.inn" /><br />
						<input :disabled="isDisabled" placeholder="Название компании"
							v-model.lazy="orderData.seller.companyName" /><br />
						<input :disabled="isDisabled" placeholder="Юр.Адресс" v-model.lazy="orderData.seller.legalAddress" /><br />
						<input :disabled="isDisabled" placeholder="Контактный телефон"
							v-model.trim.lazy="orderData.seller.mobileNumber" />
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
            <span v-show="!isDisabled" class="w-[10px] cursor-pointer" @click="removeProduct(product)">
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
        <tr v-show="!isDisabled">
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

		<table>
      <tbody>
        <tr>
          <td>Менеджер</td>
          <td class="w-2/6">
            <input :disabled="isDisabled" placeholder="Имя продавца" v-model.lazy="orderData.seller.sellerName"  />
          </td>
          <td>Покупатель</td>
          <td class="w-2/6">
            <input :disabled="isDisabled" placeholder="Имя покупателя" v-model.lazy="orderData.buyer.buyerName" />
          </td>
        </tr>
      </tbody>
		</table>
		<br />
    <textarea :disabled="isDisabled" placeholder="Комментарии" v-model.lazy="orderData.comments"
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