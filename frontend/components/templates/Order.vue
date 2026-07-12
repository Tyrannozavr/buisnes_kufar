<script setup lang="ts">
import type { OrderData, ProductsInOrder } from '~/types/order';
import { useDeals } from '~/composables/useDeals';
import type { Deal, ProductItem } from '~/types/dealState';
import { Editor, TemplateElement } from '~/constants/keys';
import { normalizeDate, normalizePrice } from '~/utils/normalize';
import { useRoute } from 'vue-router';
import { useRouter } from 'vue-router';
import { useUserStore } from '~/stores/user'; 
import { useSaveDeals } from '~/composables/useSaveDeals';
import {
	buildOrderDisplayRows,
	findLineChange,
	orderCellHighlightClass,
	orderRowHighlightClass,
} from '~/utils/orderChangeDiff';
import OrderProductPicker from '~/components/EditorMenu/OrderProductPicker.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { deals } = useDeals()


const { findDeal, lastDeal, deleteDeal, editSellerCompany, editBuyerCompany, editProductList, editProductComments } = useDeals()
const { completeSave, saveState } = useSaveDeals()
const { unitOptions, getOkeiCode } = useUnitsOfMeasurement()
const isDisabled = useTypedState(Editor.IS_DISABLED)
const clearState = useTypedState(Editor.CLEAR_STATE)
const removeDealState = useTypedState(Editor.REMOVE_DEAL)
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const orderChangeDiff = useTypedState(Editor.ORDER_CHANGE_DIFF, () => ref(null))

const displayProducts = computed(() =>
	buildOrderDisplayRows(orderData.value.products, orderChangeDiff.value),
)

const removedDisplayRows = computed(() =>
	displayProducts.value.filter((row) => row.isRemovedRow),
)

const lineChangeFor = (product: ProductsInOrder) =>
	findLineChange(orderChangeDiff.value, product)

const rowClass = (product: ProductsInOrder) =>
	orderRowHighlightClass({
		changeStatus: lineChangeFor(product)?.status,
		changedFields: lineChangeFor(product)?.changed_fields ?? [],
	})

const cellClass = (product: ProductsInOrder, field: string) =>
	orderCellHighlightClass(
		{
			changeStatus: lineChangeFor(product)?.status,
			changedFields: lineChangeFor(product)?.changed_fields ?? [],
		},
		field,
	)

const html = useTemplateRef('html')
const htmlOrder = useTypedState(TemplateElement.ORDER, () => ref(null))

//сделка для заполнения формы
const deal: Ref<Deal | undefined> = ref(undefined)

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
	if (deal.value) {

		const productList = deal.value.product.productList ?? []
    products = productList.map((product: ProductItem): ProductsInOrder => ({
      name: product.name,
      article: product.article,
      quantity: product.quantity ?? 0,
      units: product.units ?? '',
      price: product.price ?? 0,
      amount: product.amount ?? 0,
		}))
		const sellerData = deal.value.seller ?? {}
    seller = {
      companyId: sellerData.companyId,
      ownerName: sellerData.ownerName,
      companyName: sellerData.companyName,
      phone: sellerData.phone,
      legalAddress: sellerData.legalAddress,
      inn: Number(sellerData.inn) || 0,
		}
		const buyerData = deal.value.buyer ?? {}
    buyer = {
      companyId: buyerData.companyId,
      ownerName: buyerData.ownerName,
      companyName: buyerData.companyName,
      phone: buyerData.phone,
      legalAddress: buyerData.legalAddress,
      inn: Number(buyerData.inn) || 0,
    }

    orderData.value = {
      orderNumber: route.query.role === 'buyer' ? deal.value.buyerOrderNumber || '' : deal.value.sellerOrderNumber || '',
      dealId: deal.value.dealId,
      orderDate: deal.value.date,
      comments: deal.value.product.comments,
      amount: deal.value.product.amountPrice,
      amountWord: deal.value.product.amountWord,
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

	deal.value = findDeal(Number(query.dealId)) ?? undefined

	fillOrderData()
}

//заполнение формы из query при наличии данных в store
watch(
  () => [
    route.query.dealId,
    route.query.role,
    deals?.value?.length ?? 0,
    loadDealTrigger.value,
  ],
  () => fillFromQuery(),
  { immediate: true, deep: true }
)

//сохранение заказа в store при нажатии на кнопку сохранения в меню
watch(() => saveState.value,
	async () => {
		if (!saveState.value) return
		
		try {
			const dealId = orderData.value.dealId
			
			await editSellerCompany(dealId, orderData.value.seller)
			await editBuyerCompany(dealId, orderData.value.buyer)
			await editProductList(dealId, orderData.value.products)
			await editProductComments(dealId, orderData.value.comments ?? '')

			if (route.query.role === 'buyer') {
				orderData.value.amount = lastDeal?.value?.purchases?.product.amountPrice
				orderData.value.amountWord = lastDeal?.value?.purchases?.product.amountWord
			} else if (route.query.role === 'seller') {
				orderData.value.amount = lastDeal?.value?.sales?.product.amountPrice
				orderData.value.amountWord = lastDeal?.value?.sales?.product.amountWord
			}
		} finally {
			completeSave()
		}

	},
	{ deep: true }
)

//добавление товара в заказ — выбор из прайса поставщика (§3.3)
const isProductPickerOpen = ref(false)

const sellerCompanyId = computed(() => deal.value?.seller?.companyId ?? 0)

const openProductPicker = () => {
	if (!sellerCompanyId.value) return
	isProductPickerOpen.value = true
}

const addProductFromCatalog = (product: import('~/types/product').ProductResponse) => {
	const quantity = 1
	const price = product.price ?? 0
	const row: ProductsInOrder = {
		name: product.name ?? '',
		article: product.article ?? '',
		quantity,
		units: product.unit_of_measurement?.trim() || 'шт',
		price,
		amount: quantity * price,
	}
	orderData.value.products.push(row)
}

const addProduct = () => {
	openProductPicker()
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

//удаление сделки из store и сервера
const removeDeal = () => {
	deleteDeal(orderData.value.dealId)
	deal.value = undefined
	clearForm()
}

//удаление сделки при нажатии на кнопку удаления в меню
watch(() => removeDealState.value,
	() => {
		if (removeDealState.value) {
			removeDeal()
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
							v-model.trim.lazy="orderData.seller.phone" />
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
							v-model.lazy="orderData.buyer.phone" /><br />
					</td>
				</tr>
			</tbody>
		</table>

		<h1 style="font-weight: 700;" class="font-bold my-2">Заказ на поставку
			<span>{{ orderData.orderNumber }}</span>
			от {{ normalizeDate(orderData.orderDate || '') }} г.
		</h1>

    <table class="table-fixed p-5 mb-5 w-[99%] text-center" id="products">
      <colgroup>
        <col style="width: 3%">
        <col style="width: 24%">
        <col style="width: 17%">
        <col style="width: 7%">
        <col style="width: 9%">
        <col style="width: 6%">
        <col style="width: 9%">
        <col style="width: 10%">
        <col style="width: 3%">
      </colgroup>
      <thead>
        <tr>
          <td class="border"><span>№</span></td>
          <td class="border"><span>Название продукта</span></td>
          <td class="border"><span>Артикул</span></td>
          <td class="border"><span>Кол-во</span></td>
          <td class="border"><span>Ед. изм.</span></td>
          <td class="border"><span>ОКЕИ</span></td>
          <td class="border"><span>Цена</span></td>
          <td class="border"><span>Сумма</span></td>
          <td><span></span></td>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(product, index) in orderData.products"
          :key="`${product.article}-${product.name}-${index}`"
          :class="rowClass(product)"
        >
          <td class="border">
            <span>{{ index + 1 }}</span>
          </td>
          <td class="border align-top" :class="cellClass(product, 'name')">
            <textarea
              v-if="!isDisabled"
              rows="2"
              class="product-name-field w-full min-w-0 px-1 text-left text-sm resize-none"
              placeholder="Название"
              v-model.trim="product.name"
            />
            <span v-else class="product-name-field">{{ product.name }}</span>
          </td>
          <td class="border align-top" :class="cellClass(product, 'article')">
            <input
              v-if="!isDisabled"
              class="product-article-field w-full min-w-0 px-1 text-center text-sm"
              placeholder="Артикул"
              v-model.trim="product.article"
            />
            <span v-else class="product-article-field">{{ product.article }}</span>
          </td>
          <td class="border" :class="cellClass(product, 'quantity')">
            <input
              :disabled="isDisabled"
              class="w-full min-w-0 px-1 text-center text-sm"
              placeholder="Кол-во"
              v-model.number="product.quantity"
            />
          </td>
          <td class="border" :class="cellClass(product, 'units')">
            <select
              v-if="!isDisabled"
              :value="product.units"
              class="product-unit-select w-full min-w-0 px-1 text-center text-sm"
              @change="product.units = ($event.target as HTMLSelectElement).value"
            >
              <option value="">—</option>
              <option v-for="opt in unitOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
            <span v-else class="block w-full text-center text-sm">{{ product.units || '—' }}</span>
          </td>
          <td class="border">
            <span class="block w-full text-center text-sm">{{ getOkeiCode(product.units) || '—' }}</span>
          </td>
          <td class="border" :class="cellClass(product, 'price')">
            <input
              :disabled="isDisabled"
              class="w-full min-w-0 px-1 text-center text-sm"
              placeholder="Цена"
              v-model.number="product.price"
            />
          </td>
          <td class="border" :class="cellClass(product, 'amount')">
            <span>{{ product.amount }}</span>
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
        <tr
          v-for="(product, index) in removedDisplayRows"
          :key="`removed-${product.article}-${index}`"
          class="order-change-row-removed"
        >
          <td class="border order-change-removed"><span>—</span></td>
          <td class="border order-change-removed"><span>{{ product.name }}</span></td>
          <td class="border order-change-removed"><span>{{ product.article }}</span></td>
          <td class="border order-change-removed"><span>{{ product.quantity }}</span></td>
          <td class="border order-change-removed"><span>{{ product.units || '—' }}</span></td>
          <td class="border order-change-removed"><span>{{ getOkeiCode(product.units) || '—' }}</span></td>
          <td class="border order-change-removed"><span>{{ product.price }}</span></td>
          <td class="border order-change-removed"><span>{{ product.amount }}</span></td>
          <td />
        </tr>
        <tr v-show="!isDisabled">
          <td colspan="8" class="border text-left">
            <button
              type="button"
              class="w-full text-left text-gray-400 hover:text-gray-700 cursor-pointer"
              @click="addProduct()"
            >
              Добавить продукт
            </button>
          </td>
        </tr>
      </tbody>
    </table>

		<p
			:class="{ 'order-change-modified-inline': orderChangeDiff?.total_amount_changed }"
		>
			<span>Всего наименований:{{ orderData.products.length }}, на сумму:
				<span v-if="orderData.amount">{{ normalizePrice(orderData.amount) }} </span>
				p.</span>
		</p>
		<p><span class="underline underline-offset-4">{{ orderData.amountWord }}</span></p>
		<br />

		<table>
      <tbody>
        <tr>
          <td>Менеджер</td>
          <td class="w-2/6">
            <input :disabled="isDisabled" placeholder="Имя продавца" v-model.lazy="orderData.seller.ownerName"  />
          </td>
          <td>Покупатель</td>
          <td class="w-2/6">
            <input :disabled="isDisabled" placeholder="Имя покупателя" v-model.lazy="orderData.buyer.ownerName" />
          </td>
        </tr>
      </tbody>
		</table>
		<br />
		<UTooltip
			:text="isDisabled && route.query.role === 'seller' ? 'Нажмите «Редактировать» в меню справа' : ''"
			:disabled="!(isDisabled && route.query.role === 'seller')"
		>
			<textarea
				:disabled="isDisabled"
				placeholder="Комментарии"
				v-model.lazy="orderData.comments"
				class="w-full h-15 max-h-40"
				:class="{ 'order-change-modified': orderChangeDiff?.comments_changed }"
			/>
		</UTooltip>

		<OrderProductPicker
			v-model:open="isProductPickerOpen"
			:seller-company-id="sellerCompanyId"
			@select="addProductFromCatalog"
		/>
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

.product-name-field {
	display: block;
	white-space: normal;
	word-break: break-word;
	overflow-wrap: anywhere;
	text-align: left;
	line-height: 1.35;
}

.product-article-field {
	display: block;
	white-space: normal;
	word-break: break-all;
	overflow-wrap: anywhere;
	text-align: center;
	line-height: 1.35;
}

.product-unit-select {
	border: 1px solid #d4d4d4;
	border-radius: 0.375rem;
	background: #fff;
	padding: 2px 4px;
	line-height: 1.35;
}

.order-change-modified,
.order-change-modified-inline {
	background-color: #fef3c7;
}

.order-change-added {
	background-color: #dcfce7;
}

.order-change-row-added td {
	background-color: #ecfdf5;
}

.order-change-row-removed td,
.order-change-removed {
	background-color: #fee2e2;
	text-decoration: line-through;
	opacity: 0.9;
}
</style>