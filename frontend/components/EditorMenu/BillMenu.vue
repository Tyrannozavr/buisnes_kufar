<template>
	<div>
		<div class="mb-2">
			<USelectMenu placeholder="Тип документа" :items="billTypeOptions" v-model="billType" default-value="Счет на оплату" class="w-full" />
			<UCheckbox :disabled="isDisabled" label="Основание" v-model="reasonCheck" size="xl" class="mt-2" />
		</div>

		<div class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Ставка НДС" v-model="vatRateCheck" size="xl" class="mb-2" />
			<USelectMenu
					:disabled="isDisabled"
					placeholder="Ставка НДС"
					:items="vatRateOptions"
					v-model="sellerVatRate"
					class="w-full"
				/>
		</div>

		<div>
			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheck" size="xl" class="mt-2" @change="console.log(paymentTerms)" />
			<div class="flex gap-1" v-if="paymentTermsCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTerms">
			</div>
		</div>

		<div>
			<UCheckbox :disabled="isDisabled" label="Дополнительная инфорамация" v-model="additionalInfoCheck" size="xl" class="mt-2" />
		</div>
	</div>
</template>

<script setup lang="ts">
import type { SelectMenuItem } from '@nuxt/ui';
import { Editor } from '~/constants/keys';
import { useDeals } from '~/composables/useDeals';

const { deals } = useDeals()
const route = useRoute()
const billTypeOptions = ref<SelectMenuItem[]>([
	{label: 'Счет на оплату', value: 'bill'},
	{label: 'Счет-договор', value: 'bill-contract'}, 
	{label: 'Счет-оферта', value: 'bill-offer'}
])
const billType = useTypedState(Editor.BILL_TYPE)
const isDisabled = useTypedState(Editor.IS_DISABLED)

const initialSellerVatRate = ref(0)
const initialPaymentTerms = ref('')
//initial values for checkboxes
const initialVatRateCheck = ref(false)
const initialAdditionalInfoCheck = ref(false)
const initialPaymentTermsCheck = ref(false)
const initialReasonCheck = ref(false)

watch(() => [
	route.query.dealId,
	deals.value,
], () => {
	const deal = deals.value?.find((deal) => deal.dealId === Number(route.query.dealId))
	if (!deal) return
	initialPaymentTerms.value = deal.bill.paymentTerms ?? ''
	initialSellerVatRate.value = deal.seller.vatRate ?? 0
	initialVatRateCheck.value = deal.amountWithVatRate
	initialAdditionalInfoCheck.value = deal.bill.additionalInfo !== '' ? true : false
	initialPaymentTermsCheck.value = deal.bill.paymentTerms !== '' ? true : false
	initialReasonCheck.value = deal.bill.reason !== '' ? true : false
}, { immediate: true, deep: true })

const sellerVatRate = useTypedState(Editor.VAT_RATE, () => initialSellerVatRate)
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS, () => initialPaymentTerms)
//checkBoxes
const reasonCheck = useTypedState(Editor.REASON_CHECK, () => initialReasonCheck)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK, () => initialPaymentTermsCheck)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK, () => initialAdditionalInfoCheck)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK, () => initialVatRateCheck)

const vatRateOptions = ref<SelectMenuItem[]>([
	{label: 'Без НДС', value: 0},
	{label: '5%', value: 5},
	{label: '7%', value: 7}, 
	{label: '10%', value: 10},
	{label: '18%', value: 18},
	{label: '25%', value: 25},
])

</script>