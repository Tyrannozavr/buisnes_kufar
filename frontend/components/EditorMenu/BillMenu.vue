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

		<div v-if="billType.value === 'bill-contract'" :hidden="hiddenForBuyer" class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Условия договора" v-model="contractTermsCheck" size="xl" class="mb-2" @change="console.log(contractTerms)" />
			<USelectMenu
				v-if="contractTermsCheck"
				:disabled="isDisabled"
				placeholder="Условия договора"
				:items="contractTermsOptions"
				v-model="contractTerms"
				class="w-full"
				/>
		</div>

		<div :hidden="hiddenForBuyer">
			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheck" size="xl" class="mt-2" @change="console.log(paymentTerms)" />
			<div class="flex gap-1" v-if="paymentTermsCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTerms" default-value="3">
			</div>
		</div>

		<div v-if="billType.value === 'bill-contract'" :hidden="hiddenForBuyer">
			<UCheckbox :disabled="isDisabled" label="Срок поставки" v-model="deliveryTermsCheck" size="xl" class="mt-2" @change="console.log(deliveryTerms)" />
			<div class="flex gap-1" v-if="deliveryTermsCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки поставки" class="w-50 p-1 border rounded-lg" v-model="deliveryTerms" default-value="10">
			</div>
		</div>

		<div v-if="billType.value === 'bill'" :hidden="hiddenForBuyer">
			<UCheckbox :disabled="isDisabled" label="Дополнительная инфорамация" v-model="additionalInfoCheck" size="xl" class="mt-2" />
		</div>
	</div>
</template>

<script setup lang="ts">
import type { SelectMenuItem } from '@nuxt/ui';
import { Editor } from '~/constants/keys';
import { useDeals } from '~/composables/useDeals';

defineProps<{
	hiddenForBuyer?: boolean
}>()

const { findDeal } = useDeals()
const route = useRoute()
const isDisabled = useTypedState(Editor.IS_DISABLED)

const contractTermsOptions = ref<SelectMenuItem[]>([
	{ label: 'Стандартный, доставка Поставщика', value: 'standard-delivery-supplier'},
	{ label: 'Стандартный, доставка Покупателя', value: 'standard-delivery-buyer' },
])
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

const initialContractTerms = ref<{value: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'; label: string}>({value: 'standard-delivery-supplier', label: 'Стандартный, доставка Поставщика'})
const initialSellerVatRate = ref(0)
const initialPaymentTerms = ref('')
const initialDeliveryTerms = ref('')
//initial values for checkboxes
const initialContractTermsCheck = ref(false)
const initialVatRateCheck = ref(false)
const initialAdditionalInfoCheck = ref(false)
const initialPaymentTermsCheck = ref(false)
const initialDeliveryTermsCheck = ref(false)
const initialReasonCheck = ref(false)

const dealForEditor = computed(() =>
	findDeal(Number(route.query.dealId))
)

watch(
	[() => route.query.dealId, dealForEditor],
	() => {
		const deal = dealForEditor.value
		if (!deal) return
		initialContractTermsCheck.value = deal.bill.contractTermsText !== '' ? true : false
		initialContractTerms.value.value = deal.bill.contractTerms ?? 'standard-delivery-supplier'

		initialPaymentTerms.value = deal.bill.paymentTerms ?? ''
		initialPaymentTermsCheck.value = deal.bill.paymentTerms !== '' ? true : false
		initialDeliveryTerms.value = deal.bill.deliveryTerms ?? ''
		initialDeliveryTermsCheck.value = deal.bill.deliveryTerms !== '' ? true : false

		initialSellerVatRate.value = deal.seller.vatRate ?? 0
		initialVatRateCheck.value = deal.amountWithVatRate
		initialAdditionalInfoCheck.value = deal.bill.additionalInfo !== '' ? true : false
		initialReasonCheck.value = deal.bill.reason !== '' ? true : false
	},
	{ immediate: true }
)

const billType = useTypedState(Editor.BILL_TYPE)
const contractTerms = useTypedState(Editor.CONTRACT_TERMS, () => initialContractTerms)
const contractTermsCheck = useTypedState(Editor.CONTRACT_TERMS_CHECK, () => initialContractTermsCheck)
const sellerVatRate = useTypedState(Editor.VAT_RATE, () => initialSellerVatRate)
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS, () => initialPaymentTerms)
const deliveryTerms = useTypedState(Editor.DELIVERY_TERMS, () => initialDeliveryTerms)
//checkBoxes
const reasonCheck = useTypedState(Editor.REASON_CHECK, () => initialReasonCheck)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK, () => initialPaymentTermsCheck)
const deliveryTermsCheck = useTypedState(Editor.DELIVERY_TERMS_CHECK, () => initialDeliveryTermsCheck)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK, () => initialAdditionalInfoCheck)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK, () => initialVatRateCheck)

watch(contractTerms, () => {
	console.log(contractTerms.value)
})


</script>