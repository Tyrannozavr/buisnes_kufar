<script setup lang="ts">
import { Editor } from '~/constants/keys';

const templateEditorOpen = ref(false)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const conditionNumber = ref(0)






const openTemplateEditor = () => {
	templateEditorOpen.value = true
}

const countConditions = (text: string): number => {
	if (!text) {
		return 0
	}
	const conditions = text.match(/^\d+/gm)
	const maxCondition = Math.max(...(conditions?.map(c => Number(c)) ?? []))
	if (maxCondition === -Infinity) {
		return 0
	}
	return maxCondition
}

const addCondition = () => {
	conditionNumber.value++

}

const closeSupplyContractEditor = () => {
	templateEditorOpen.value = false
}

const saveSupplyContract = () => {
	templateEditorOpen.value = false
}

const useDefaultTemplate = () => {
	
}

//подсчет пунктов текста
watch(() => [], () => {
	
}, { deep: true })









</script>

<template>
	<UModal
		title="Редактор договора поставки"
		v-model:open="templateEditorOpen"
		:dismissible="false"
		:ui="{
			content: 'max-w-5xl h-full',
			footer: 'justify-end'
		}"
	>
		<UButton
			:disabled="isDisabled"
			label="Редактор шаблона договора поставки"
			color="neutral"
			variant="subtle"
			@click="openTemplateEditor()"
		/>

		<template #body>
			<div class="flex flex-col gap-3">

				<!-- Меню для счета-договора -->	
				<div class="flex justify-between">
					<div class="flex gap-2 w-4/5">
						<USelect
							class="w-1/3"
							placeholder="Название шаблона"
						/>
						<UCheckbox
							size="xl"
							class="w-2/3 self-center"
							label="Использовать шаблон по умолчанию"
							@click="useDefaultTemplate()"
						/>
					</div>

					<div class="flex gap-2 self-center">
						<!-- <UButton
							icon="i-lucide-x"
							label="Отмена"
							color="neutral"
							variant="subtle"
							@click="closeSupplyContractEditor()"
						/> -->
						<UButton
							icon="i-lucide-check"
							label="Сохранить"
							color="primary"
							variant="subtle"
							@click="saveSupplyContract()"
						/>
					</div>
				</div>

				<!-- Инструменты редактора -->
				<UCard class="flex w-full mb-3" variant="subtle">
					<div>
						
					</div>
				</UCard>


				<!-- Текстовое поле -->
				<div class="w-full h-full">
					<textarea
						id="textarea"
						class="w-full h-full bg-gray-100 p-4 rounded-xl resize-none"
						placeholder="Введите условия договора"
						@keydown.enter.prevent="addCondition()"
					/>
				</div>

			</div>
		</template>
	</UModal>
</template>