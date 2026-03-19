<template>
	<div>
		<div class="mb-2">
			<USelectMenu placeholder="Тип документа" :items="typeOfDocumentOptions" v-model="typeOfDocument" class="w-full" />
			<UCheckbox :disabled="isDisabled" label="Основание" v-model="reasonCheck" size="xl" class="mt-2" />
		</div>

		<div class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Ставка НДС" v-model="vatRateCheck" size="xl" class="mb-2" />
		</div>

		<div>
			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheck" size="xl" class="mt-2" @change="console.log(paymentTerms)" />
			<div class="flex gap-1" v-if="paymentTermsCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTerms">
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
const typeOfDocumentOptions = ref<SelectMenuItem[]>([
	{label: 'Счет на оплату', id: 'bill'},
	{label: 'Счет-договор', id: 'bill-contract'}, 
	{label: 'Счет-оферта', id: 'bill-offert'}
])
const typeOfDocument = ref()
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS, () => ref(''))
const isDisabled = useTypedState(Editor.IS_DISABLED)
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

	initialVatRateCheck.value = deal.amountWithVatRate
	initialAdditionalInfoCheck.value = deal.bill.additionalInfo !== '' ? true : false
	initialPaymentTermsCheck.value = deal.bill.paymentTerms !== '' ? true : false
	initialReasonCheck.value = deal.bill.reason !== '' ? true : false
}, { immediate: true, deep: true })



//checkBoxes
const reasonCheck = useTypedState(Editor.REASON_CHECK, () => initialReasonCheck)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK, () => initialPaymentTermsCheck)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK, () => initialAdditionalInfoCheck)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK, () => initialVatRateCheck)



</script>