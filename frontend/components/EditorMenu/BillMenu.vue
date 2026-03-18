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
			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="dueDateCheck" size="xl" class="mt-2" @change="console.log(dueDate)" />
			<div class="flex gap-1" v-if="dueDateCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="dueDate">
			</div>
		</div>

		<div>
			<UCheckbox :disabled="isDisabled" label="Дополнительная инфорамация" v-model="additionalInfo" size="xl" class="mt-2" />
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
const dueDate = useState(Editor.DUE_DATE, () => ref())
const initialVatRateCheck = ref(false)
const isDisabled = useTypedState(Editor.IS_DISABLED)

watch(() => [
	route.query.dealId,
	deals.value,
], () => {
	const deal = deals.value?.find((deal) => deal.dealId === Number(route.query.dealId))
	if (!deal) return
	initialVatRateCheck.value = deal.amountWithVatRate
	console.log(initialVatRateCheck.value)
}, { immediate: true, deep: true })

//checkBoxes
const reasonCheck = useTypedState(Editor.REASON_CHECK, () => ref(false))
const dueDateCheck = useTypedState(Editor.DUE_DATE_CHECK, () => ref(false))
const additionalInfo = useTypedState(Editor.ADDITIOANAL_INFO, () => ref(false))
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK, () => initialVatRateCheck)



</script>