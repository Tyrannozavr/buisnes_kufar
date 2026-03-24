<template>
	<div class="font-sans text-l text-justify text-pretty w-full">
		<table class="p-3 w-full border-2 border-black">
			<tbody>
				<tr>
					<td colspan="4" rowspan="1">
						<textarea placeholder="OФП, Название компании, город" :disabled="isDisabled" class="w-full" v-model="billData.buyer.companyName"/>
						<br />
						<br />
						<br />
						<br />
					</td>
					<td class="border">БИК</td>
					<td>
						<textarea placeholder="номер БИК" :disabled="isDisabled" class="w-full" v-model="billData.buyer.bic"/>
					</td>
				</tr>

				<tr class="border-b-2 black">
					<td colspan="4" class="border">
						<textarea placeholder="Банк получателя" :disabled="isDisabled" class="w-full" v-model="billData.buyer.bankName"/>
					</td>
					<td class="border">Сч. №</td>
					<td>
						<textarea placeholder="номер счёта" :disabled="isDisabled" class="w-full" v-model="billData.buyer.accountNumber"/>
					</td>
				</tr>

				<tr>
					<td class="border w-12">ИНН</td>
					<td class="border">
						<textarea placeholder="ИНН" :disabled="isDisabled" class="w-full" v-model="billData.seller.inn"/>
					</td>
					<td class="border w-12">КПП</td>
					<td class="border">
						<textarea placeholder="КПП" :disabled="isDisabled" class="w-full" v-model="billData.seller.kpp"/>
					</td>
					<td rowspan="3" class="border">Сч. №</td>
					<td rowspan="3">
						<textarea placeholder="Расчетный счёт" :disabled="isDisabled" class="w-full" v-model="billData.seller.accountNumber"/>
					</td>
				</tr>

				<tr>
					<td colspan="4">
						<textarea placeholder="ОФП, Название компании" :disabled="isDisabled" class="w-full" v-model="billData.seller.companyName"/>
						<br>
						<br>
						<br>
					</td>
				</tr>

				<tr>
					<td colspan="4" class="border">
						<textarea placeholder="Получатель" :disabled="isDisabled" class="w-full" v-model="billData.buyer.companyName"/>
					</td>
				</tr>
			</tbody>
		</table>

		<h2 class="font-bold text-2xl">{{ billTypeSelected.label }} № {{ billData.number || '—' }} от {{ normalizeDate(billData.date) || '—' }} г.</h2>
		<hr class="border-2">
		<br>
		<table>
			<tbody>
			<tr>
				<td>
					<p>Поставщик 
						<br>
						(исполнитель):</p>
				</td>
				<td>
					<textarea placeholder="Поставщик" :disabled="isDisabled" class="w-full font-bold" :value="billData.seller.companyName ? `${billData.seller.companyName}, ${billData.seller.inn}, ${billData.seller.kpp}, ${billData.seller.index}, ${billData.seller.legalAddress}` : ''"/>
				</td>
			</tr>
			<tr>
				<td>
					<p>Покупатель 
						<br>
						(заказчик):</p>
				</td>
				<td>
					<textarea placeholder="Покупатель" :disabled="isDisabled" class="w-full font-bold" :value="billData.buyer.companyName ? `${billData.buyer.companyName}, ${billData.buyer.inn}, ${billData.buyer.kpp}, ${billData.buyer.index}, ${billData.buyer.legalAddress}` : ''"/>
				</td>
			</tr>
			<tr v-if="reasonCheck">
				<td>
					<p>Основание: </p>
				</td>
				<td>
					<textarea placeholder="Основание" :disabled="isDisabled" class="w-full font-bold" v-model="billData.reason"/>
				</td>
			</tr>
			</tbody>
		</table>

		<br>

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
				<tr v-for="product in billData.products">
					<td class="border">
						<span>{{ billData.products.indexOf(product) + 1 }}</span>
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
						<span class="">{{ normalizePrice(product.amount) }}</span>
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

				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2" >Итого:</td>
					<td >
						<span class="font-bold">{{ normalizePrice(billData.products.reduce((acc: number, product: ProductsInOrder) => acc + product.amount, 0)) }}</span>
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2">В том числе НДС:</td>
					<td>
						<span class="font-bold">{{ normalizePrice(billData.amountVatRate) }}</span>
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="4"></td>
					<td colspan="2">Всего к оплате:</td>
					<td>
						<span class="font-bold">{{ normalizePrice(billData.amount) }}</span>
					</td>
				</tr>
				
			</tbody> 
		</table>

		<p>
			<span>
				Всего наименований: 
				<span class="font-bold">
					{{ billData.products.length }}
				</span>
				, на сумму:
				<span class="font-bold">
					{{ normalizePrice(billData.amount) }} p.
				</span> 
			</span>
		</p>
		<div>
			<span class="underline underline-offset-4">
				<span class="font-bold">{{ amountWord }}</span>
			</span>
		</div>


		<div v-if="billType === 'bill'">
			<div v-if="paymentTermsCheck">
				<p>
					<span>Срок оплаты: 
						<span class="font-bold">
							{{ billData.paymentTerms }} рабочих дней
						</span>
					</span>
				</p>
			</div>

			<br>

			<p v-if="additionalInfoCheck">
			<textarea class="w-full h-50 overflow-hidden resize-none" v-model="billData.additionalInfo" />
			</p>

			<br>
			<hr class="border-2">
			<br>

			<table class="w-full border-separate border-spacing-y-3 border-spacing-x-0">
				<tbody >
					<tr v-for="official in billData.officials" :key="official.id" class="w-full">
						<td class="w-1/3">
							<input :disabled="isDisabled" class="w-full" placeholder="Должность" v-model="official.position"/>
						</td>
						<td class="w-1/3">
							<input :disabled="isDisabled" class="w-full pb-0 pt-2" placeholder="Имя" v-model="official.name"/>
						</td>
						<td class="border-b w-full">
						</td>
						<td>
							<span :hidden="isDisabled" class="w-[10px] cursor-pointer" @click="removePerson(official)">
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
					<tr v-if="officials.length < 3" :hidden="isDisabled" class="w-full">
						<td colspan="4">
							<PersonSelector :isDisabled="isDisabled" @addPerson="addPerson($event)" />
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<br>

		<div v-if="billType === 'bill-contract'">
			<BillContract :billData="billData" />
		</div>

		<div v-if="billType === 'bill-offer'">
			<BillOffer :billData="billData" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { Editor } from '~/constants/keys';
import { useRoute, useRouter } from 'vue-router';
import { useDeals } from '~/composables/useDeals';
import { normalizeDate } from '~/utils/normalize';
import type { BillData } from '~/types/bill';
import { TemplateElement } from '~/constants/keys';
import { useUserStore } from '~/stores/user';
import type { ProductItem } from '~/types/dealState';
import type { ProductsInOrder } from '~/types/order';
import type { OfficialBill } from '~/types/bill';
import PersonSelector from '~/components/tables/PersonSelector.vue';
import numberToWordsRu from 'number-to-words-ru';
import { useSaveDeals } from '~/composables/useSaveDeals';
import BillContract from './Bill-Contract.vue';
import BillOffer from './Bill-Offer.vue';

const { deals, findDeal, deleteDeal, editSellerCompany, editBuyerCompany, editProductList, editBillReason, editPaymentTerms, editAdditionalInfo, editOfficialsBill, editAmountWithVatRate, editVatRateSeller, editAmountVatRate, editContractTerms, editContractTermsText, editDeliveryTerms } = useDeals()

const reasonCheck = useTypedState(Editor.REASON_CHECK)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK)
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS)
const deliveryTermsCheck = useTypedState(Editor.DELIVERY_TERMS_CHECK)
const deliveryTerms = useTypedState(Editor.DELIVERY_TERMS)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const sellerVatRate = useTypedState(Editor.VAT_RATE)
const contractTerms = useTypedState(Editor.CONTRACT_TERMS)
const contractTermsCheck = useTypedState(Editor.CONTRACT_TERMS_CHECK)

const billTypeSelected = useTypedState(Editor.BILL_TYPE, () => ref({value: 'bill', label: 'Счет на оплату'}))
const billType = computed(() => billTypeSelected.value.value)


const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const clearState = useTypedState(Editor.CLEAR_STATE)
const removeDealState = useTypedState(Editor.REMOVE_DEAL)
const { completeSave, saveState } = useSaveDeals()

const html = useTemplateRef('html')
const htmlBill = useTypedState(TemplateElement.BILL, () => ref(null))

let seller: BillData['seller'] = {}
let buyer: BillData['buyer'] = {}
let products: BillData['products'] = []
let officials: BillData['officials'] = []

const billData = ref<BillData>({
	dealId: 0,
	number: '',
	date: '',
	amount: 0,
	amountVatRate: 0,
	amountWord: '',
	seller: {
		vatRate: 0,
	},
	buyer,
	paymentTerms: '',
	deliveryTerms: '',
	additionalInfo: '',
	contractTerms: 'standard-delivery-supplier',
	contractTermsText: '',
	reason: '',
	products,
	officials,
})

//заполнение условий договора
watch(() => [contractTerms, contractTermsCheck, billData.value.paymentTerms, billData.value.deliveryTerms],
	() => {
		if (contractTermsCheck.value) {
			billData.value.contractTerms = contractTerms.value.value

			if (contractTerms.value.value === 'standard-delivery-supplier') {
				billData.value.contractTermsText = `Основные условия настоящего договора-счета № ${billData.value.number || '—'} от ${normalizeDate(billData.value.date) || '—'} г.
1. 	Предметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. 	Оплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.	
3. 	Настоящий Счет-договор действителен в течение ${billData.value.paymentTerms} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. 	Поставщик обязан доставить оплаченный товар и передать его Покупателю в течение ${billData.value.deliveryTerms} рабочих дней с момента зачисления оплаты на расчетный счет
5. 	Оплаченный товар доставляется Покупателю силами ПОСТАВЩИКА
6. 	Оплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. 	Поставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. 	Покупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. 	Подписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара.`

			} else if (contractTerms.value.value === 'standard-delivery-buyer') {
				billData.value.contractTermsText = `Основные условия настоящего договора-счета № ${billData.value.number || '—'} от ${normalizeDate(billData.value.date) || '—'} г.
1. 	Предметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. 	Оплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.	
3. 	Настоящий Счет-договор действителен в течение ${billData.value.paymentTerms} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. 	Поставщик обязан доставить оплаченный товар и передать его Покупателю в течение ${billData.value.deliveryTerms} рабочих дней с момента зачисления оплаты на расчетный счет
5. 	Оплаченный товар доставляется Покупателю силами ПОКУПАТЕЛЯ
6. 	Оплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. 	Поставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. 	Покупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. 	Подписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара.`

			} else if (contractTerms.value.value === 'custom') {
				const deal = findDeal(Number(route.query.dealId))
				const dealContractTermsText = deal?.bill.contractTermsText
				billData.value.contractTermsText = dealContractTermsText ?? ''
			}
		} else {
			billData.value.contractTerms = 'standard-delivery-supplier'
			billData.value.contractTermsText = ''
		}
	},
	{ deep: true }
)

//заполнение срока поставки
watch(() => [deliveryTermsCheck, deliveryTerms], () => {
	if (deliveryTermsCheck.value) {
		billData.value.deliveryTerms = deliveryTerms.value
	} else {
		billData.value.deliveryTerms = '10'
	}
}, { deep: true })

//заполнение срока оплаты
watch(() => [paymentTermsCheck, paymentTerms], () => {
	if (paymentTermsCheck.value) {
		billData.value.paymentTerms = paymentTerms.value
	} else {
		billData.value.paymentTerms = '3'
	}
}, { deep: true })

//заполнение основания
watch(reasonCheck, () => {
	const deal = findDeal(Number(route.query.dealId))
	const dealReason = deal?.bill.reason
	if (reasonCheck.value && dealReason) {
		billData.value.reason = dealReason
		return dealReason
	} else if (reasonCheck.value && !dealReason) {
		const reason = `Заказ №${deal?.sellerOrderNumber || ''} от ${normalizeDate(deal?.date || '')} г.`
		billData.value.reason = reason
		return reason
	}
})

//заполнение дополнительной информации
watch(additionalInfoCheck, () => { 
	const deal = findDeal(Number(route.query.dealId))
	const dealAdditionalInfo = deal?.bill.additionalInfo

	if (additionalInfoCheck.value && dealAdditionalInfo) {
		billData.value.additionalInfo = dealAdditionalInfo
		 return dealAdditionalInfo
	} else if (additionalInfoCheck.value && !dealAdditionalInfo) {
		const additionalInfo = `Внимание!
Оплата данного счета означает согласие с условиями поставки товара.
Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.
Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности и паспорта.
Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.
Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности и паспорта.`
		billData.value.additionalInfo = additionalInfo
		return additionalInfo
	}
})

//рассчет суммы и суммы НДС
watch(() => [
	sellerVatRate.value,
	vatRateCheck.value,
	route.query.dealId
], () => {
	const amountTable = products.reduce((acc: number, product: ProductsInOrder) => acc + product.amount, 0)
	const isAmountWithVatRate = findDeal(Number(route.query.dealId))?.amountWithVatRate ?? false
	billData.value.seller.vatRate = sellerVatRate.value

	if (vatRateCheck.value && isAmountWithVatRate) {

		billData.value.amount = amountTable + (amountTable * ((normalizeVatRate(sellerVatRate.value)) ?? 0) / 100)
		billData.value.amountVatRate = amountTable * ((normalizeVatRate(sellerVatRate.value)) ?? 0) / 100

	} else if (vatRateCheck.value && !isAmountWithVatRate) {
		billData.value.amount = amountTable + (amountTable * ((normalizeVatRate(sellerVatRate.value)) ?? 0) / 100)
		billData.value.amountVatRate = amountTable * ((normalizeVatRate(sellerVatRate.value)) ?? 0) / 100

	} else if (!vatRateCheck.value && isAmountWithVatRate) {
		billData.value.amount = amountTable
		billData.value.amountVatRate = 0

	} else if (!vatRateCheck.value && !isAmountWithVatRate) {
		billData.value.amount = amountTable
		billData.value.amountVatRate = 0
	}
}, { immediate: true, deep: true })

//рассчет суммы словами
const amountWord = computed<string>(() => {
	return numberToWordsRu.convert(billData.value.amount, {
		showNumberParts: {
			fractional: true
		},
		convertNumberToWords: {
			fractional: false
		},
		showCurrency: {
			integer: true,
			fractional: true
		}
	})
})

//добавление должностного лица в счет
const addPerson = (person: OfficialBill) => {
	if (billData.value.officials.some((p: OfficialBill) => p.id === person.id)) return
	billData.value.officials.push(person)
}

//удаление должностного лица из счета
const removePerson = (person: OfficialBill) => {
	billData.value.officials = billData.value.officials.filter((p: OfficialBill) => p.id !== person.id)
}

//заполнение query параметров по данным в форме
const fillQuery = () => {
  const query: Record<string, any> = {...route.query}

  if (billData.value.dealId) {
    query.dealId = String(billData.value.dealId)
  }

  if (userStore.companyId === billData.value.buyer.companyId) {
		query.role = 'buyer'
  } else if (userStore.companyId === billData.value.seller.companyId) {
		query.role = 'seller'
  }

  router.replace({
    query,
    hash: '#bill'
  })
} 

//заполнение формы по данным сделки
const fillBillData = () => {
	const deal = findDeal(Number(route.query.dealId))
	if (deal) {

		const productList = deal.product.productList ?? []
    products = productList.map((product: ProductItem): ProductsInOrder => ({
      name: product.name,
      article: product.article,
      quantity: product.quantity ?? 0,
      units: product.units ?? '',
      price: product.price ?? 0,
      amount: product.amount ?? 0,
		}))
		const sellerData = deal.seller ?? {}
    seller = {
      ownerName: sellerData.ownerName,
      companyName: sellerData.companyName,
      companyId: sellerData.companyId,
      phone: sellerData.phone,
			legalAddress: sellerData.legalAddress,
			index: sellerData.index,
			inn: Number(sellerData.inn) || 0,
			kpp: sellerData.kpp,
			accountNumber: sellerData.accountNumber,
			correspondentBankAccount: sellerData.correspondentBankAccount,
			bankName: sellerData.bankName,
			bic: sellerData.bic,
			vatRate: sellerData.vatRate,
		}
		const buyerData = deal.buyer ?? {}
    buyer = {
      ownerName: buyerData.ownerName,
      companyName: buyerData.companyName,
			companyId: buyerData.companyId,
			phone: buyerData.phone,
			legalAddress: buyerData.legalAddress,
			index: buyerData.index,
			inn: Number(buyerData.inn) || 0,
			kpp: buyerData.kpp,
			accountNumber: buyerData.accountNumber,
			correspondentBankAccount: buyerData.correspondentBankAccount,
			bankName: buyerData.bankName,
			bic: buyerData.bic,
			vatRate: buyerData.vatRate,
		}
		const officialsData = deal.bill.officials ?? []
		officials = officialsData.map((official: OfficialBill): OfficialBill => ({
			id: official.id ,
			position: official.position,
			name: official.name,
		}))

    billData.value = {
      number: deal.bill.number,
      dealId: deal.dealId,
      date: deal.billDate,
      reason: deal.bill.reason,
      amount: deal.product.amountPrice,
			amountVatRate: deal.product.amountVatRate,
			amountWord: deal.product.amountWord,
			paymentTerms: deal.bill.paymentTerms,
			deliveryTerms: deal.bill.deliveryTerms,
			additionalInfo: deal.bill.additionalInfo,
			contractTerms: deal.bill.contractTerms,
			contractTermsText: deal.bill.contractTermsText,
      seller,
      buyer,
      products: [...products],
      officials: [...officials],
    }
	} 
  fillQuery()
}

//заполнение формы по данным сделки из query
const fillFromQuery = () => {
	const query = route.query
	if (!query?.dealId || !query?.role) return

	fillBillData()
}

//заполнение формы из query при наличии данных в store
watch(
  () => [
    route.query.dealId,
		deals?.value?.length ?? 0,
		findDeal(Number(route.query.dealId))?.bill.number ?? ''
  ],
  () => fillFromQuery(),
  { immediate: true, deep: true }
)

//сохранение заказа в store при нажатии на кнопку сохранения в меню
watch(() => saveState,
	async () => {
		if (!saveState.value) return
		try {
			const dealId = billData.value.dealId

			if (route.query.role === 'seller') {
				await editAmountWithVatRate(dealId, vatRateCheck.value)
				await editVatRateSeller(dealId, (normalizeVatRate(billData.value.seller.vatRate) ?? 0))
				await editAmountVatRate(dealId, billData.value.amountVatRate)
				await editSellerCompany(dealId, billData.value.seller) 
				await editBuyerCompany(dealId, billData.value.buyer)
				await editProductList(dealId, billData.value.products)
				await editContractTerms(dealId, billData.value.contractTerms)
				await editContractTermsText(dealId, billData.value.contractTermsText)
				await editPaymentTerms(dealId, billData.value.paymentTerms)
				await editDeliveryTerms(dealId, billData.value.deliveryTerms)
				await editAdditionalInfo(dealId, billData.value.additionalInfo)
				await editBillReason(dealId, billData.value.reason)
				await editOfficialsBill(dealId, billData.value.officials)
			}
		} finally { 
			completeSave()
		}
	},
	{ deep: true }
)

//добавление товара в счет в компоненте
const addProduct = () => {
	const product: ProductsInOrder = {
		name: '',
		article: '',
		quantity: 0,
		units: '',
		price: 0,
		amount: 0,
	}
	billData.value.products.push(product)
}

//очистка формы
const clearForm = () => {
	products = []
  seller = {}
	buyer = {}
	officials = []

	billData.value = {
		number: '',
		dealId: 0,
		amount: 0,
		amountVatRate: 0,
		amountWord: '',
		date: '',
		reason: '',
		paymentTerms: '',
		deliveryTerms: '',
		additionalInfo: '',
		contractTerms: 'standard-delivery-supplier',
		contractTermsText: '',
		seller,
		buyer,
		products,
		officials,
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
	deleteDeal(billData.value.dealId)
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

//удаление товара из счета в компоненте
const removeProduct = (product: ProductsInOrder): void => {
	const index = billData.value.products.indexOf(product)
	billData.value.products.splice(index, 1)
}

//заполнение htmlBill
onMounted(() => {
	htmlBill.value = html.value
})
</script>

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
	line-height: 1.75;
	padding: 1px 5px;
	vertical-align: middle;
	field-sizing: content;
}
</style>