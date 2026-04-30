<script setup lang="ts">
import SupplyContractEditor from '~/components/EditorMenu/templatesEditors/SupplyContractEditor.vue'
import { Editor } from '~/constants/keys'

const coverLetterCheck = useTypedState(Editor.COVER_LETTER_CHECK, () => ref(false))
const supplierDetailsCheck = useTypedState(Editor.SUPPLIER_DETAILS_CHECK, () => ref(false))
const buyerDetailsCheck = useTypedState(Editor.BUYER_DETAILS_CHECK, () => ref(false))

// mocks
const supplyContractTemplates = ref([
	{
		label: 'Шаблон 1',
		value: 'template1'
	},
	{
		label: 'Шаблон 2',
		value: 'template2'
	}
])
const supplyContractTemplate = ref()
</script>

<template>
	<div class="flex flex-col gap-2">
		<SupplyContractEditor />

		<USelect
			placeholder="Выберите шаблон договора поставки"
			:items="supplyContractTemplates"
			v-model="supplyContractTemplate"
		/>

		<UCheckbox
			label="Колонтитул"
			size="xl"
			v-model="coverLetterCheck"
		/>
		<UCheckbox
			label="Реквизиты поставщика"
			size="xl"
			v-model="supplierDetailsCheck"
		/>
		<UCheckbox
			label="Реквизиты покупателя"
			size="xl"
			v-model="buyerDetailsCheck"
		/>
	</div>
</template>