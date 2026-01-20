<template>
	<div>
		<div class="mb-2">
			<USelectMenu placeholder="Тип документа" :items="typeOfDocumentOptions" v-model="typeOfDocument" class="w-full" />
			<UCheckbox label="Основание" v-model="reason" size="xl" class="mt-2" />
		</div>

		<div class="mb-2">
			<UCheckbox label="Ставка НДС" v-model="vatRateCheck" size="xl" class="mb-2" />
			<USelectMenu :disabled="!vatRateCheck" placeholder="Ставка НДС" :items="vatRateOptions" v-model="vatRate" class="w-full" />
		</div>

		<div>
			<UCheckbox label="Срок оплаты" v-model="dueDateCheck" size="xl" class="mt-2" @change="console.log(dueDate)" />
			<div class="flex gap-1" v-if="dueDateCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="dueDate">
			</div>
			<!-- <br> -->
			<!-- <UCalendar v-if="dueDateCheck" v-model="dueDate" variant="subtle"/> -->
		</div>

		<div>
			<UCheckbox label="Дополнительная инфорамация" v-model="additionalInfo" size="xl" class="mt-2" />
		</div>
	</div>
</template>

<script setup lang="ts">
import type { SelectMenuItem } from '@nuxt/ui';
import { Editor } from '~/constants/keys';

const typeOfDocumentOptions = ref<SelectMenuItem[]>([
	{label: 'Счет на оплату', id: 'bill'},
	{label: 'Счет-договор', id: 'bill-contract'}, 
	{label: 'Счет-оферта', id: 'bill-offert'}
])
const typeOfDocument = ref()
const vatRateOptions = ref<SelectMenuItem[]>([
	{label: '5%', id: '5'},
	{label: '7%', id: '7'}, 
	{label: '10%', id: '10'},
	{label: '18%', id: '18'},
	{label: '25%', id: '25'},
])
const vatRate = useState(Editor.VAT_RATE, () => ref())
const dueDate = useState(Editor.DUE_DATE, () => ref())

//checkBoxes
const reason = useState<boolean>(Editor.REASON, () => ref(false))
const dueDateCheck = useState<boolean>(Editor.DUE_DATE_CHECK, () => ref(false))
const additionalInfo = useState(Editor.ADDITIOANAL_INFO, () => ref(false))
const vatRateCheck = useState(Editor.VAT_RATE_CHECK, () => ref(false))

</script>

<style scoped></style>