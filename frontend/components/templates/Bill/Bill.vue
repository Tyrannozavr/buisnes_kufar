<template>
	<div ref="html" class="font-sans text-l text-justify text-pretty w-full">
		<table class="p-3 w-full border-2 border-black">
			<tbody>
				<tr>
					<td colspan="4" rowspan="1">
						<textarea placeholder="Наименование банка" :disabled="isDisabled" class="w-full" v-model="billData.seller.bankName"/>
						<br />
						<br />
						<br />
						<br />
					</td>
					<td class="border">БИК</td>
					<td>
						<textarea placeholder="номер БИК" :disabled="isDisabled" class="w-full" v-model="billData.seller.bic"/>
					</td>
				</tr>

				<tr class="border-b-2 black">
					<td colspan="4" class="border">
						<textarea placeholder="Банк получателя" :disabled="isDisabled" class="w-full" v-model="billData.seller.bankName"/>
					</td>
					<td class="border">Сч. №</td>
					<td>
						<textarea placeholder="корр. счёт" :disabled="isDisabled" class="w-full" v-model="billData.seller.correspondentBankAccount"/>
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
						<textarea placeholder="Получатель" :disabled="isDisabled" class="w-full" :value="sellerRecipientLine"/>
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
					<textarea placeholder="Поставщик" :disabled="isDisabled" class="w-full font-bold" :value="sellerPartyLine"/>
				</td>
			</tr>
			<tr>
				<td>
					<p>Покупатель 
						<br>
						(заказчик):</p>
				</td>
				<td>
					<textarea placeholder="Покупатель" :disabled="isDisabled" class="w-full font-bold" :value="buyerPartyLine"/>
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
				<tr v-for="product in billData.products">
					<td class="border">
						<span>{{ billData.products.indexOf(product) + 1 }}</span>
					</td>
					<td class="border align-top">
						<textarea
							v-if="!isDisabled"
							rows="2"
							class="product-name-field w-full min-w-0 px-1 text-left text-sm resize-none"
							placeholder="Название"
							v-model.lazy="product.name"
						/>
						<span v-else class="product-name-field">{{ product.name }}</span>
					</td>
					<td class="border align-top">
						<input
							v-if="!isDisabled"
							class="product-article-field w-full min-w-0 px-1 text-center text-sm"
							placeholder="Артикул"
							v-model.lazy="product.article"
						/>
						<span v-else class="product-article-field">{{ product.article }}</span>
					</td>
					<td class="border">
						<input :disabled="isDisabled" class="w-full min-w-0 px-1 text-center text-sm" placeholder="Кол-во"
							v-model.lazy="product.quantity" />
					</td>
					<td class="border">
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
					<td class="border">
						<input :disabled="isDisabled" class="w-full min-w-0 px-1 text-center text-sm" placeholder="Цена" v-model.lazy="product.price" />
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
					<td @click="addProduct()" colspan="8"
						class="border text-left text-gray-400 hover:text-gray-700 cursor-pointer">
						Добавить товар
					</td>
				</tr>

				<tr class="text-right">
					<td colspan="5"></td>
					<td colspan="2" >Итого:</td>
					<td >
						<span class="font-bold">{{ normalizePrice(billData.amountExclVat) }}</span>
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="5"></td>
					<td colspan="2">В том числе НДС:</td>
					<td>
						<span class="font-bold">{{ vatRateCheck ? normalizePrice(billData.amountVatRate) : '' }}</span>
					</td>
				</tr>
				<tr class="text-right">
					<td colspan="5"></td>
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
					{{ normalizePrice(billData.amount) }} руб.
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
					Счет действителен в течении
					<span class="font-bold">{{ billData.paymentTerms }}</span>
					рабочих дней с момента выставления
				</p>
			</div>

			<br>

			<div v-if="additionalInfoCheck">
				<textarea
					v-if="!isDisabled"
					class="w-full min-h-24 text-sm"
					v-model="billData.additionalInfo"
					placeholder="Дополнительная информация"
				/>
				<template v-else>
					<p v-for="(line, idx) in billData.additionalInfo.split('\n')" :key="idx">{{ line }}</p>
				</template>
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
							<span :hidden="isDisabled" class="w-2.5 cursor-pointer" @click="removePerson(official)">
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
					<tr v-if="billData.officials.length < 3" :hidden="isDisabled" class="w-full">
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
import { useCompanyBillRequisites } from '~/composables/useCompanyBillRequisites';
import { useBillFillState } from '~/composables/useBillFillState';
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
import { formatCompanyPartyLine, formatCompanyRecipientLine } from '~/utils/companyPartyLine';

const { deals, findDeal, deleteDeal, editSellerCompany, editBuyerCompany, editProductList, editBillReason, editPaymentTerms, editAdditionalInfo, editOfficialsBill, editAmountWithVatRate, editVatRateSeller, editAmountVatRate, editContractTermsContract, editContractTermsTextContract, editDeliveryTermsContract, editPaymentTermsContract, editContractTermsOffer, editContractTermsTextOffer, editAdditionalInfoOffer, editPaymentTermsOffer, editAmountExclVat } = useDeals()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { completeSave, saveState } = useSaveDeals()
const { unitOptions, getOkeiCode } = useUnitsOfMeasurement()
const { loadBillRequisites, mergeDealPartyRequisites } = useCompanyBillRequisites()
const { billAwaitingFill, clearBillAwaitingFill } = useBillFillState()
const isDisabled = useTypedState(Editor.IS_DISABLED)
const clearState = useTypedState(Editor.CLEAR_STATE)
const removeDealState = useTypedState(Editor.REMOVE_DEAL)
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const billType = computed(() => billTypeSelected.value.value)

const html = useTemplateRef('html')
const htmlBill = useTypedState(TemplateElement.BILL, () => ref(null))

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
	amountExclVat: 0,
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
const applyAdditionalInfoFromCheck = () => {
	const deal = findDeal(Number(route.query.dealId))
	const dealAdditionalInfo = deal?.bill.additionalInfo

	if (!additionalInfoCheck.value) {
		billData.value.additionalInfo = ''
		return
	}
	billData.value.additionalInfo = dealAdditionalInfo || ADDITIONAL_INFO_BILL.PAYMENT
}

watch(additionalInfoCheck, applyAdditionalInfoFromCheck, { immediate: true })

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

// рассчёт суммы по позициям: источник правды — billData.products (не внешний `products`, он расходится после fillBillData / addProduct)
const recalcBillAmounts = (): void => {
	const rows = billData.value.products
	let amountTable = 0
	for (const product of rows) {
		const qty = Number(product.quantity) || 0
		const price = Number(product.price) || 0
		const line = qty * price
		product.amount = line
		amountTable += line
	}
	const isAmountWithVatRate = findDeal(Number(route.query.dealId))?.amountWithVatRate ?? false
	billData.value.seller.vatRate = sellerVatRate.value
	billData.value.amountExclVat = amountTable

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
}

watch(
	() => ({
		products: billData.value.products,
		sellerVat: sellerVatRate.value,
		vatCheck: vatRateCheck.value,
		dealId: route.query.dealId,
	}),
	() => recalcBillAmounts(),
	{ deep: true, immediate: true }
)

//рассчет суммы словами
const sellerRecipientLine = computed(() => formatCompanyRecipientLine(billData.value.seller))

const sellerPartyLine = computed(() => formatCompanyPartyLine(billData.value.seller))
const buyerPartyLine = computed(() => formatCompanyPartyLine(billData.value.buyer))

const amountWord = computed<string>(() => {
	if (billData.value.amountWord?.trim()) {
		return billData.value.amountWord
	}
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

//заполнение формы только номером и датой счёта (после createBill, §1.3)
const fillBillMinimalData = () => {
	const deal = findDeal(Number(route.query.dealId))
	if (!deal) return

	billData.value = {
		dealId: deal.dealId,
		number: deal.bill.number,
		date: deal.billDate ?? '',
		amount: 0,
		amountExclVat: 0,
		amountVatRate: 0,
		amountWord: '',
		reason: '',
		products: [],
		seller: { vatRate: 0 },
		buyer: {},
		officials: [],
		paymentTerms: '',
		additionalInfo: '',
		paymentTermsContract: '',
		deliveryTermsContract: '',
		contractTermsContract: 'standard-delivery-supplier',
		contractTermsTextContract: '',
		paymentTermsOffer: '',
		contractTermsOffer: 'standard-delivery-supplier',
		contractTermsTextOffer: '',
		additionalInfoOffer: '',
	}
	applyAdditionalInfoFromCheck()
	fillQuery()
}

//заполнение формы по данным сделки
const fillBillData = async () => {
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
      companyType: sellerData.companyType,
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
			companyType: buyerData.companyType,
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
			isBase: official.isBase,
			baseDocument: official.baseDocument,
			baseDocumentName: official.baseDocumentName,
		}))

		if (route.query.role === 'seller') {
			const fresh = await loadBillRequisites(seller.companyId)
			if (fresh) {
				seller = mergeDealPartyRequisites(seller, fresh.party)
				if (!officials.length) {
					officials = [...fresh.officials]
				}
			}
		}

    billData.value = {
      number: deal.bill.number,
      dealId: deal.dealId,
			amount: deal.product.amountPrice,
			amountExclVat: deal.totalAmountExclVat,
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
		applyAdditionalInfoFromCheck()
	}
  fillQuery()
}

//заполнение формы по данным сделки из query
const fillFromQuery = async () => {
	const query = route.query
	if (!query?.dealId || !query?.role) return

	const deal = findDeal(Number(query.dealId))
	if (deal && !deal.billDate && !deal.bill?.number) {
		clearBillAwaitingFill(deal.dealId)
	}

	if (billAwaitingFill.value) {
		fillBillMinimalData()
		return
	}

	await fillBillData()
}

//заполнение формы из query при наличии данных в store
watch(
  () => [
    route.query.dealId,
    route.query.role,
		deals?.value?.length ?? 0,
		findDeal(Number(route.query.dealId))?.bill.number ?? '',
    loadDealTrigger.value,
		billAwaitingFill.value,
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
				await editAmountExclVat(dealId, billData.value.amountExclVat)
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

//очистка формы (§5: номер и дата сохраняются)
const clearForm = () => {
	const preserved = {
		dealId: billData.value.dealId,
		number: billData.value.number,
		date: billData.value.date,
	}
	products = []
	seller = { vatRate: 0 }
	buyer = {}
	officials = []

	billData.value = {
		...preserved,
		amount: 0,
		amountExclVat: 0,
		amountVatRate: 0,
		amountWord: '',
		reason: '',
		products,
		seller,
		buyer,
		officials,
		paymentTerms: '',
		additionalInfo: '',
		paymentTermsContract: '',
		deliveryTermsContract: '',
		contractTermsContract: 'standard-delivery-supplier',
		contractTermsTextContract: '',
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

watch(billData, () => {
	htmlBill.value = html.value
}, { deep: true })
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
</style>