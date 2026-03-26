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

			<div v-if="additionalInfoCheck">
				<p v-for="line in billData.additionalInfo.split('\n')">{{ line }}</p>
			</div>

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
					<tr v-if="billData.officials.length === 0">
						<td colspan="4">
							<div class="w-2/5 mt-6">
								<div class="h-5"></div>
								<div class="text-center text-xs border-t">(должность, подпись, ФИО)</div>
							</div>
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
			<BillOffer :billData :additionalInfoCheckOffer />
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
import { CONTRACT_TERMS_BILL_OFFER, CONTRACT_TERMS_BILL_CONTRACT, ADDITIONAL_INFO_BILL } from '~/constants/contractTerms';

const { deals, findDeal, deleteDeal, editSellerCompany, editBuyerCompany, editProductList, editBillReason, editPaymentTerms, editAdditionalInfo, editOfficialsBill, editAmountWithVatRate, editVatRateSeller, editAmountVatRate, editContractTermsContract, editContractTermsTextContract, editDeliveryTermsContract, editPaymentTermsContract, editContractTermsOffer, editContractTermsTextOffer, editAdditionalInfoOffer, editPaymentTermsOffer } = useDeals()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { completeSave, saveState } = useSaveDeals()
const isDisabled = useTypedState(Editor.IS_DISABLED)
const clearState = useTypedState(Editor.CLEAR_STATE)
const removeDealState = useTypedState(Editor.REMOVE_DEAL)
const billType = computed(() => billTypeSelected.value.value)

const html = useTemplateRef('html')
const htmlBill = useTypedState(TemplateElement.BILL, () => ref(null)
)
//bill-general
const billTypeSelected = useTypedState(Editor.BILL_TYPE, () => ref({value: 'bill', label: 'Счет на оплату'}))
const reasonCheck = useTypedState(Editor.REASON_CHECK)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK)
const sellerVatRate = useTypedState(Editor.VAT_RATE)

//bill-payment(счет-оплата)
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK)

//bill-contract
const paymentTermsContract = useTypedState(Editor.PAYMENT_TERMS_CONTRACT)
const deliveryTermsContract = useTypedState(Editor.DELIVERY_TERMS_CONTRACT)
const contractTermsContract = useTypedState(Editor.CONTRACT_TERMS_CONTRACT)
const contractTermsTextContract = useTypedState(Editor.CONTRACT_TERMS_TEXT_CONTRACT)
const paymentTermsCheckContract = useTypedState(Editor.PAYMENT_TERMS_CHECK_CONTRACT)
const deliveryTermsCheckContract = useTypedState(Editor.DELIVERY_TERMS_CHECK_CONTRACT)
const contractTermsCheckContract = useTypedState(Editor.CONTRACT_TERMS_CHECK_CONTRACT)

//bill-offer
const paymentTermsOffer = useTypedState(Editor.PAYMENT_TERMS_OFFER)
const contractTermsOffer = useTypedState(Editor.CONTRACT_TERMS_OFFER)
const contractTermsTextOffer = useTypedState(Editor.CONTRACT_TERMS_TEXT_OFFER)
const contractTermsCheckOffer = useTypedState(Editor.CONTRACT_TERMS_CHECK_OFFER)
const paymentTermsCheckOffer = useTypedState(Editor.PAYMENT_TERMS_CHECK_OFFER)
const additionalInfoCheckOffer = useTypedState(Editor.ADDITIONAL_INFO_CHECK_OFFER)



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
	reason: '',
	products,
	seller: {
		vatRate: 0,
	},
	buyer,
	officials,
	//bill-payment
	paymentTerms: '',
	additionalInfo: '',
	//bill-contract
	paymentTermsContract: '',
	deliveryTermsContract: '',
	contractTermsContract: 'standard-delivery-supplier',
	contractTermsTextContract: '',
	//bill-offer
	paymentTermsOffer: '',
	contractTermsOffer: 'standard-delivery-supplier',
	contractTermsTextOffer: '',
	additionalInfoOffer: '',
})

//установка значений сроков оплаты и доставки по умолчанию, если они есть в шаблоне
watch(() => [
	contractTermsTextContract.value,
	contractTermsTextOffer.value,
	contractTermsContract.value,
	contractTermsOffer.value,
], () => {
	if ((contractTermsTextContract.value?.includes('{{ СРОК_ОПЛАТЫ_СЧЕТА_ДОГОВОРА }}') && contractTermsContract.value.value === 'custom')) {
		paymentTermsCheckContract.value = true
		paymentTermsContract.value = '3'
	}
	if ((contractTermsTextContract.value?.includes('{{ СРОК_ПОСТАВКИ_СЧЕТА_ДОГОВОРА }}') && contractTermsContract.value.value === 'custom')) {
		deliveryTermsCheckContract.value = true
		deliveryTermsContract.value = '10'
	}
	if ((contractTermsTextOffer.value?.includes('{{ СРОК_ОПЛАТЫ_СЧЕТА_ОФЕРТЫ }}') && contractTermsOffer.value.value === 'custom')) {
		paymentTermsCheckOffer.value = true
		paymentTermsOffer.value = '3'
	}
}, { deep: true, immediate: true })

//заполнение условий договора счета-оферты
watch(() => [
	contractTermsOffer,
	contractTermsTextOffer,
	contractTermsCheckOffer,
	billData.value.paymentTermsOffer,
	paymentTermsCheckOffer
],
	() => {
		if (contractTermsCheckOffer.value) {
			billData.value.contractTermsOffer = contractTermsOffer.value.value

			if (contractTermsOffer.value.value === 'standard-delivery-supplier' && paymentTermsCheckOffer.value) {

				billData.value.contractTermsTextOffer = CONTRACT_TERMS_BILL_OFFER.DELIVERY_SUPPLIER_PAYMENT(
					billData.value.paymentTermsOffer,
					billData.value.seller.productionAddress ?? '______________'
				)
			} else if (contractTermsOffer.value.value === 'standard-delivery-buyer' && paymentTermsCheckOffer.value) {

				billData.value.contractTermsTextOffer = CONTRACT_TERMS_BILL_OFFER.DELIVERY_BUYER_PAYMENT(
					billData.value.paymentTermsOffer,
					billData.value.seller.productionAddress ?? '______________'
				)
			} else if (contractTermsOffer.value.value === 'standard-delivery-supplier' && !paymentTermsCheckOffer.value) {

				billData.value.contractTermsTextOffer = CONTRACT_TERMS_BILL_OFFER.DELIVERY_SUPPLIER_WITHOUT_PAYMENT(
					billData.value.seller.productionAddress ?? '______________'
				)
			} else if (contractTermsOffer.value.value === 'standard-delivery-buyer' && !paymentTermsCheckOffer.value) {

				billData.value.contractTermsTextOffer = CONTRACT_TERMS_BILL_OFFER.DELIVERY_BUYER_WITHOUT_PAYMENT(
					billData.value.seller.productionAddress ?? '______________'
				)
			} else if (contractTermsOffer.value.value === 'custom' && contractTermsTextOffer.value) {

				billData.value.contractTermsTextOffer = contractTermsTextOffer.value
			}
		} else {
			billData.value.contractTermsTextOffer = ''
		}
	}, { deep: true, immediate: true }
)

//заполнение условий договора счета-договора
watch(() => [
	contractTermsContract.value,
	contractTermsTextContract.value,
	contractTermsCheckContract.value,
	billData.value.paymentTermsContract,
	billData.value.deliveryTermsContract,
	paymentTermsCheckContract.value,
	deliveryTermsCheckContract.value
],
	() => {
		if (contractTermsCheckContract.value) {
			billData.value.contractTermsContract = contractTermsContract.value.value

			if (contractTermsContract.value.value === 'standard-delivery-supplier' && paymentTermsCheckContract.value && deliveryTermsCheckContract.value) {

				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_SUPPLIER_WITH_PAYMENT_AND_DELIVERY(
					billData.value.number,
					normalizeDate(billData.value.date),
					billData.value.paymentTermsContract,
					billData.value.deliveryTermsContract)

			} else if (contractTermsContract.value.value === 'standard-delivery-buyer' && paymentTermsCheckContract.value && deliveryTermsCheckContract.value) {

				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_BUYER_WITH_PAYMENT_AND_DELIVERY(
					billData.value.number,
					normalizeDate(billData.value.date),
					billData.value.paymentTermsContract,
					billData.value.deliveryTermsContract
				)

			} else if (contractTermsContract.value.value === 'standard-delivery-supplier' && !paymentTermsCheckContract.value && deliveryTermsCheckContract.value) {

				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_SUPPLIER_WITHOUT_PAYMENT_AND_DELIVERY(
					billData.value.number,
					normalizeDate(billData.value.date)
				)
			} else if (contractTermsContract.value.value === 'standard-delivery-supplier' && paymentTermsCheckContract.value && !deliveryTermsCheckContract.value)
			{
				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_SUPPLIER_ONLY_PAYMENT(
					billData.value.number,
					normalizeDate(billData.value.date),
					billData.value.paymentTermsContract)

			} else if (contractTermsContract.value.value === 'standard-delivery-buyer' && !paymentTermsCheckContract.value && deliveryTermsCheckContract.value) {

				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_BUYER_ONLY_DELIVERY(
					billData.value.number,
					normalizeDate(billData.value.date),
					billData.value.deliveryTermsContract)

			} else if (contractTermsContract.value.value === 'standard-delivery-buyer' && paymentTermsCheckContract.value && !deliveryTermsCheckContract.value) {

				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_BUYER_ONLY_PAYMENT(
					billData.value.number,
					normalizeDate(billData.value.date),
					billData.value.paymentTermsContract)

			} else if (contractTermsContract.value.value === 'standard-delivery-buyer' && !paymentTermsCheckContract.value && !deliveryTermsCheckContract.value) {

				billData.value.contractTermsTextContract = CONTRACT_TERMS_BILL_CONTRACT.DELIVERY_BUYER_WITHOUT_PAYMENT_AND_DELIVERY(
					billData.value.number,
					normalizeDate(billData.value.date)
				)
			

			} else if (contractTermsContract.value.value === 'custom' && contractTermsTextContract.value) {

				billData.value.contractTermsTextContract = contractTermsTextContract.value
			}
		} else {
			billData.value.contractTermsTextContract = ''
		}
	},
	{ deep: true, immediate: true }
)

//заполнение срока поставки счета-договора
watch(() => [deliveryTermsCheckContract, deliveryTermsContract],
	() => {
	if (deliveryTermsCheckContract.value) {
		billData.value.deliveryTermsContract = deliveryTermsContract.value
	} else {
		billData.value.deliveryTermsContract = ''
	}
}, { deep: true }
)

//заполнение срока оплаты счета-оплаты
watch(() => [paymentTermsCheck, paymentTerms],
	() => {
	if (paymentTermsCheck.value) {
		billData.value.paymentTerms = paymentTerms.value
	} else {
		billData.value.paymentTerms = ''
	}
}, { deep: true }
)

//заполнение срока оплаты и доставки счета-договора
watch(() => [
	paymentTermsCheckContract,
	paymentTermsContract,
	deliveryTermsCheckContract,
	deliveryTermsContract
], () => {
	if (paymentTermsCheck.value) {
		billData.value.paymentTerms = paymentTerms.value
	} else {
		billData.value.paymentTerms = ''
	}

	if (deliveryTermsCheckContract) {
		billData.value.deliveryTermsContract = deliveryTermsContract.value
	} else {
		billData.value.deliveryTermsContract = ''
	}
}, { deep: true }
)

//заполнение срока оплаты счета-оплаты
watch(() => [paymentTermsCheck, paymentTerms], () => {
	if (paymentTermsCheck.value) {
		billData.value.paymentTerms = paymentTerms.value
	} else {
		billData.value.paymentTerms = ''
	}
}, { deep: true }
)

//заполнение срока оплаты счета-договора
watch(() => [paymentTermsCheckContract, paymentTermsContract], () => {
	if (paymentTermsCheckContract.value) {
		billData.value.paymentTermsContract = paymentTermsContract.value
	} else {
		billData.value.paymentTermsContract = ''
	}
}, { deep: true }
)

//заполнение срока оплаты счета-оферты
watch(() => [paymentTermsCheckOffer, paymentTermsOffer], () => {
	if (paymentTermsCheckOffer.value) {
		billData.value.paymentTermsOffer = paymentTermsOffer.value
	} else {
		billData.value.paymentTermsOffer = ''
	}
}, { deep: true }
)

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

//заполнение дополнительной информации счета-оплаты
watch(additionalInfoCheck, () => { 
	const deal = findDeal(Number(route.query.dealId))
	const dealAdditionalInfo = deal?.bill.additionalInfo

	if (additionalInfoCheck.value && dealAdditionalInfo) {
		billData.value.additionalInfo = dealAdditionalInfo
		 return dealAdditionalInfo
	} else if (additionalInfoCheck.value && !dealAdditionalInfo) {
		const additionalInfo = ADDITIONAL_INFO_BILL.PAYMENT
		billData.value.additionalInfo = additionalInfo
		return additionalInfo
	}
})

//заполнение дополнительной информации счета-офферты
watch(additionalInfoCheckOffer, () => { 
	const deal = findDeal(Number(route.query.dealId))
	const dealAdditionalInfoOffer = deal?.bill.additionalInfoOffer

	if (additionalInfoCheckOffer.value && dealAdditionalInfoOffer) {
		billData.value.additionalInfoOffer = dealAdditionalInfoOffer
		 return dealAdditionalInfoOffer
	} else if (additionalInfoCheckOffer.value && !dealAdditionalInfoOffer) {
		const additionalInfoOffer = ADDITIONAL_INFO_BILL.OFFER(billData.value.seller.companyName ?? `______________`)
		billData.value.additionalInfoOffer = additionalInfoOffer
		return additionalInfoOffer
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
}, { immediate: true, deep: true }
)

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
			productionAddress: sellerData.productionAddress,
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
			productionAddress: buyerData.productionAddress,
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
      amount: deal.product.amountPrice,
			amountVatRate: deal.product.amountVatRate,
			amountWord: deal.product.amountWord,
      date: deal.billDate,
      reason: deal.bill.reason,
      products: [...products],
      seller,
      buyer,
			officials: [...officials],
			//bill-payment
			paymentTerms: deal.bill.paymentTerms,
			additionalInfo: deal.bill.additionalInfo,

			//bill-contract
			paymentTermsContract: deal.bill.paymentTermsContract,
			deliveryTermsContract: deal.bill.deliveryTermsContract,
			contractTermsContract: deal.bill.contractTermsContract,
			contractTermsTextContract: deal.bill.contractTermsTextContract,

			//bill-offer
			paymentTermsOffer: deal.bill.paymentTermsOffer,
			contractTermsOffer: deal.bill.contractTermsOffer,
			contractTermsTextOffer: deal.bill.contractTermsTextOffer,
			additionalInfoOffer: deal.bill.additionalInfoOffer,
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
				await editProductList(dealId, billData.value.products)
				await editBuyerCompany(dealId, billData.value.buyer)
				await editSellerCompany(dealId, billData.value.seller) 

				await editAmountVatRate(dealId, billData.value.amountVatRate)
				await editAmountWithVatRate(dealId, vatRateCheck.value)
				await editVatRateSeller(dealId, (normalizeVatRate(billData.value.seller.vatRate) ?? 0))
				await editOfficialsBill(dealId, billData.value.officials)

				await editBillReason(dealId, billData.value.reason)
				await editPaymentTerms(dealId, billData.value.paymentTerms)
				await editAdditionalInfo(dealId, billData.value.additionalInfo)

				await editContractTermsContract(dealId, billData.value.contractTermsContract)
				await editDeliveryTermsContract(dealId, billData.value.deliveryTermsContract)
				await editContractTermsTextContract(dealId, billData.value.contractTermsTextContract)
				await editPaymentTermsContract(dealId, billData.value.paymentTermsContract)

				await editPaymentTermsOffer(dealId, billData.value.paymentTermsOffer)
				await editContractTermsOffer(dealId, billData.value.contractTermsOffer)
				await editContractTermsTextOffer(dealId, billData.value.contractTermsTextOffer)
				await editAdditionalInfoOffer(dealId, billData.value.additionalInfoOffer)
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
		dealId: 0,
		number: '',
		date: '',
		amount: 0,
		amountVatRate: 0,
		amountWord: '',
		reason: '',
		products,
		seller: {
			vatRate: 0,
		},
		buyer,
		officials,
		//bill-payment
		paymentTerms: '',
		additionalInfo: '',
		//bill-contract
		paymentTermsContract: '',
		deliveryTermsContract: '',
		contractTermsContract: 'standard-delivery-supplier',
		contractTermsTextContract: '',
		//bill-offer
		paymentTermsOffer: '',
		contractTermsOffer: 'standard-delivery-supplier',
		contractTermsTextOffer: '',
		additionalInfoOffer: '',
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