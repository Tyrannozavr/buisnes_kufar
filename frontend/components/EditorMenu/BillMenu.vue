<template>
	<div>
		<USelectMenu placeholder="Тип документа" :items="billTypeOptions" v-model="billType" default-value="Счет на оплату" class="w-full" />

		<div :hidden="hiddenForBuyer" class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Основание" v-model="reasonCheck" size="xl" class="mt-2" />
		</div>

		<div :hidden="hiddenForBuyer" class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Ставка НДС" v-model="vatRateCheck" size="xl" class="mb-2" />
			<USelectMenu
				v-if="vatRateCheck"
				:disabled="isDisabled"
				placeholder="Ставка НДС"
				:items="vatRateOptions"
				v-model="sellerVatRate"
				class="w-full"
				/>
		</div>

		<div v-if="billType.value === 'bill'" :hidden="hiddenForBuyer" class="flex flex-col gap-2">
			<UCheckbox :disabled="isDisabled" label="Дополнительная инфорамация" v-model="additionalInfoCheck" size="xl" />

			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheck" size="xl"/>
			<div class="flex gap-1" v-if="paymentTermsCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTerms" default-value="3">
			</div>
		</div>
		
		<div v-if="billType.value === 'bill-contract'" :hidden="hiddenForBuyer" class="flex flex-col gap-2">
			<div class="flex gap-2 justify-between">
				<UCheckbox :disabled="isDisabled" label="Условия договора" v-model="contractTermsCheckContract" size="xl"/>

				<ContractTermsEditor />
			</div>

			<USelectMenu
				v-if="contractTermsCheckContract"
				:disabled="isDisabled"
				placeholder="Условия договора"
				:items="contractTermsOptionsContract"
				v-model="contractTermsContract"
				class="w-full"
				/>

			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheckContract" size="xl"/>
			<div class="flex gap-1" v-if="paymentTermsCheckContract">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTermsContract" default-value="3">
			</div>

			<UCheckbox :disabled="isDisabled" label="Срок поставки" v-model="deliveryTermsCheckContract" size="xl"/>
			<div class="flex gap-1" v-if="deliveryTermsCheckContract">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки поставки" class="w-50 p-1 border rounded-lg" v-model="deliveryTermsContract" default-value="10">
			</div>
		</div>

		<div v-if="billType.value === 'bill-offer'" :hidden="hiddenForBuyer" class="flex flex-col gap-2">
			<UCheckbox :disabled="isDisabled" label="Дополнительная информация" v-model="additionalInfoCheckOffer" size="xl"/>

			<div class="flex gap-2 justify-between">
				<UCheckbox :disabled="isDisabled" label="Условия договора" v-model="contractTermsCheckOffer" size="xl"/>

				<ContractTermsEditor />
			</div>

			<USelectMenu
				v-if="contractTermsCheckOffer"
				:disabled="isDisabled"
				placeholder="Условия договора"
				:items="contractTermsOptionsOffer"
				v-model="contractTermsOffer"
				class="w-full"
				/>

			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheckOffer" size="xl"/>
			<div class="flex gap-1" v-if="paymentTermsCheckOffer">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTermsOffer" default-value="3">
			</div>
		</div>

	</div>
</template>

<script setup lang="ts">
import type { SelectMenuItem } from '@nuxt/ui';
import { Editor } from '~/constants/keys';
import { useDeals } from '~/composables/useDeals';
import ContractTermsEditor from '~/components/EditorMenu/ContractTermsEditor.vue';

defineProps<{
	hiddenForBuyer?: boolean
}>()

const { findDeal } = useDeals()
const route = useRoute()
const isDisabled = useTypedState(Editor.IS_DISABLED)

const billTypeOptions = ref<SelectMenuItem[]>([
	{label: 'Счет на оплату', value: 'bill'},
	{label: 'Счет-договор', value: 'bill-contract'}, 
	{label: 'Счет-оферта', value: 'bill-offer'}
])
const vatRateOptions = ref<SelectMenuItem[]>([
	{label: 'Без НДС', value: 0},
	{label: '5%', value: 5},
	{label: '7%', value: 7}, 
	{label: '10%', value: 10},
	{label: '18%', value: 18},
	{label: '25%', value: 25},
])
const contractTermsOptionsContract = ref<SelectMenuItem[]>([
	{ label: 'Стандартный, доставка Поставщика', value: 'standard-delivery-supplier'},
	{ label: 'Стандартный, доставка Покупателя', value: 'standard-delivery-buyer' },
	{ label: 'Свой шаблон', value: 'custom' },
])
const contractTermsOptionsOffer = ref<SelectMenuItem[]>([
	{ label: 'Стандартный, доставка Поставщика', value: 'standard-delivery-supplier'},
	{ label: 'Стандартный, доставка Покупателя', value: 'standard-delivery-buyer' },
	{ label: 'Свой шаблон', value: 'custom' },
])

//initial values
const initialReasonCheck = ref(false)
const initialVatRateCheck = ref(false)
const initialSellerVatRate = ref(0)

//bill-payment(счет-оплата)
const initialPaymentTerms = ref('')
const initialPaymentTermsCheck = ref(false)
const initialAdditionalInfoCheck = ref(false)

//bill-contract
const initialPaymentTermsContract = ref('')
const initialDeliveryTermsContract = ref('')
const initialContractTermsContract = ref<{ value: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'; label: string }>({ value: 'standard-delivery-supplier', label: 'Стандартный, доставка Поставщика' })
const initialPaymentTermsCheckContract = ref(false)
const initialDeliveryTermsCheckContract = ref(false)
const initialContractTermsCheckContract = ref(false)

//bill-offer
const initialPaymentTermsOffer = ref('')
const initialContractTermsOffer = ref<{ value: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'; label: string }>({ value: 'standard-delivery-supplier', label: 'Стандартный, доставка Поставщика' })
const initialContractTermsCheckOffer = ref(false)
const initialPaymentTermsCheckOffer = ref(false)
const initialAdditionalInfoCheckOffer = ref(false)

const dealForEditor = computed(() =>
	findDeal(Number(route.query.dealId))
)

watch(
	[() => route.query.dealId, dealForEditor],
	() => {
		const deal = dealForEditor.value
		if (!deal) return
		//bill-general
		initialReasonCheck.value = deal.bill.reason !== '' ? true : false
		initialVatRateCheck.value = deal.amountWithVatRate
		initialSellerVatRate.value = deal.seller.vatRate ?? 0

		//bill-payment(счет-оплата)
		initialPaymentTerms.value = deal.bill.paymentTerms ?? ''
		initialPaymentTermsCheck.value = deal.bill.paymentTerms !== '' ? true : false
		initialAdditionalInfoCheck.value = deal.bill.additionalInfo !== '' ? true : false

		//bill-contract
		initialPaymentTermsContract.value = deal.bill.paymentTermsContract ?? ''
		initialDeliveryTermsContract.value = deal.bill.deliveryTermsContract ?? ''
		initialContractTermsContract.value.value = deal.bill.contractTermsContract ?? 'standard-delivery-supplier'
		initialPaymentTermsCheckContract.value = deal.bill.paymentTermsContract !== '' ? true : false
		initialDeliveryTermsCheckContract.value = deal.bill.deliveryTermsContract !== '' ? true : false
		initialContractTermsCheckContract.value = deal.bill.contractTermsTextContract !== '' ? true : false

		//bill-offer
		initialPaymentTermsOffer.value = deal.bill.paymentTermsOffer ?? ''
		initialContractTermsOffer.value.value = deal.bill.contractTermsOffer ?? 'standard-delivery-supplier'
		initialContractTermsCheckOffer.value = deal.bill.contractTermsTextOffer !== '' ? true : false
		initialPaymentTermsCheckOffer.value = deal.bill.paymentTermsOffer !== '' ? true : false
		initialAdditionalInfoCheckOffer.value = deal.bill.additionalInfoOffer !== '' ? true : false
	},
	{ immediate: true }
)

//bill-general
const billType = useTypedState(Editor.BILL_TYPE)
const reasonCheck = useTypedState(Editor.REASON_CHECK, () => initialReasonCheck)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK, () => initialVatRateCheck)
const sellerVatRate = useTypedState(Editor.VAT_RATE, () => initialSellerVatRate)

//bill-payment(счет-оплата)
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS, () => initialPaymentTerms)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK, () => initialPaymentTermsCheck)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK, () => initialAdditionalInfoCheck)

//bill-contract
const paymentTermsContract = useTypedState(Editor.PAYMENT_TERMS_CONTRACT, () => initialPaymentTermsContract)
const deliveryTermsContract = useTypedState(Editor.DELIVERY_TERMS_CONTRACT, () => initialDeliveryTermsContract)
const contractTermsContract = useTypedState(Editor.CONTRACT_TERMS_CONTRACT, () => initialContractTermsContract)
const paymentTermsCheckContract = useTypedState(Editor.PAYMENT_TERMS_CHECK_CONTRACT, () => initialPaymentTermsCheckContract)
const deliveryTermsCheckContract = useTypedState(Editor.DELIVERY_TERMS_CHECK_CONTRACT, () => initialDeliveryTermsCheckContract)
const contractTermsCheckContract = useTypedState(Editor.CONTRACT_TERMS_CHECK_CONTRACT, () => initialContractTermsCheckContract)


//bill-offer
const paymentTermsOffer = useTypedState(Editor.PAYMENT_TERMS_OFFER, () => initialPaymentTermsOffer)
const contractTermsOffer = useTypedState(Editor.CONTRACT_TERMS_OFFER, () => initialContractTermsOffer)
const contractTermsCheckOffer = useTypedState(Editor.CONTRACT_TERMS_CHECK_OFFER, () => initialContractTermsCheckOffer)
const paymentTermsCheckOffer = useTypedState(Editor.PAYMENT_TERMS_CHECK_OFFER, () => initialPaymentTermsCheckOffer)
const additionalInfoCheckOffer = useTypedState(Editor.ADDITIONAL_INFO_CHECK_OFFER, () => initialAdditionalInfoCheckOffer)
</script>