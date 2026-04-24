<script setup lang="ts">
import SupplyContractEditor from '~/components/EditorMenu/templatesEditors/SupplyContractEditor.vue'

const coverLetterCheck = ref(false)
const supplierDetailsCheck = ref(false)
const buyerDetailsCheck = ref(false)
</script>

<template>
	<div class="flex flex-col gap-2">
		<!-- TODO: Тут нужно создать новый компонент редактирования Шаблонов, который будет опираться на договор поставки -->
		<SupplyContractEditor />

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