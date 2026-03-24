<script setup lang="ts">
import type { SelectMenuItem } from "@nuxt/ui"
import { Editor } from "~/constants/keys"

const isDisabled = useTypedState(Editor.IS_DISABLED)
const templateEditorOpen = ref(false)
const contractTermsText = useTypedState(Editor.CONTRACT_TERMS_TEXT)
const contractTermsCheck = useTypedState(Editor.CONTRACT_TERMS_CHECK)
const customContractTermsText = ref("")
const selectedContractTerms = ref<{ label: string, value: string }>({ label: "Свой шаблон", value: "custom" })
const conditionNumber = ref(0)

const contractTermsOptions = ref<SelectMenuItem[]>([
	{
		label: "Стандартный",
		value: "standard"
	},
	{ label: "Новый шаблон", value: "new-template" }
])

const openTemplateEditor = () => {
	templateEditorOpen.value = true
}

const closeTemplateEditor = () => {
	templateEditorOpen.value = false
	customContractTermsText.value = ''
}

const saveContractTerms = () => {
	contractTermsText.value = customContractTermsText.value
	templateEditorOpen.value = false
}

const countConditions = (text: string): number => {
	const conditions = text.match(/^\d+/gm)
	const maxCondition = Math.max(...(conditions?.map(c => Number(c)) ?? []))
	if (maxCondition === -Infinity) {
		return 0
	}
	return maxCondition
}

const addCondition = () => {
	conditionNumber.value++
	customContractTermsText.value += `\n${conditionNumber.value}.\t`
}

const insertField = ( field: string) => {
	const textarea = document.getElementById('textarea') as HTMLTextAreaElement

	const start = textarea.selectionStart
	const end = textarea.selectionEnd
	const before = textarea.value.substring(0, start)
	const after = textarea.value.substring(end)
	customContractTermsText.value = before + field + after

	nextTick(() => {
		textarea.focus()
		const position = start + field.length
		textarea.setSelectionRange(position, position)
	})
}

//подсчет пунктов текста
watch(() => [customContractTermsText.value], () => {
	conditionNumber.value = countConditions(customContractTermsText.value)
}, { deep: true })

//вставка шаблона для редактирования
watch(() => [selectedContractTerms], () => {
	if (selectedContractTerms.value.value === 'standard') {
		customContractTermsText.value = `Основные условия настоящего договора-счета № {{ НОМЕР_СЧЕТА }} от {{ ДАТА }}
1. 	Предметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. 	Оплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.	
3. 	Настоящий Счет-договор действителен в течение {{ СРОК_ОПЛАТЫ }} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. 	Поставщик обязан доставить оплаченный товар и передать его Покупателю в течение {{ СРОК_ПОСТАВКИ }} рабочих дней с момента зачисления оплаты на расчетный счет
5. 	Оплаченный товар доставляется Покупателю силами ПОСТАВЩИКА/ПОКУПАТЕЛЯ
6. 	Оплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. 	Поставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. 	Покупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. 	Подписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара.`

	} else if (selectedContractTerms.value.value === 'new-template') {
		customContractTermsText.value = 'Введите условия договора'
	}
}, { deep: true })
</script>

<template>
	<UModal
		v-if="contractTermsCheck"
		title="Редактор условий договора"
		description="Задайте свои условия договора, на основании других шаблонов или создайте свой"
		v-model:open="templateEditorOpen"
		:dismissible="false"
		:ui="{
			content: 'max-w-5xl h-full',
			footer: 'justify-end'
		}"
	>
		<UButton
			:disabled="isDisabled"
			label="Редактор шаблона"
			color="neutral"
			variant="subtle"
			@click="openTemplateEditor()"
		/>

		<template #body>
			<div class="flex gap-5 h-full">

				<!-- Текстовое поле -->
				<div class="w-2/3">
					<textarea
						id="textarea"
						class="w-full h-full bg-gray-100 p-4 rounded-xl resize-none"
						v-model="customContractTermsText"
						placeholder="Введите условия договора"
						@keydown.enter.prevent="addCondition()"
					/>
				</div>

				<!-- Меню -->
				<div class="max-w-1/3 min-w-1/3">
					<UCard class="flex flex-col gap-2 h-full" variant="subtle">
						<div class="flex flex-col gap-2">
							<div>
								<p class="text-sm text-gray-500">Выберите шаблон, на основании которого будут сгенерированы условия договора</p>
							</div>
							<div>
								<USelectMenu
									placeholder="Выберите шаблон"
									:items="contractTermsOptions"
									v-model="selectedContractTerms"
									class="w-full"
								/>
							</div>
							<div>
								<p class="text-sm text-gray-500">Вставьте поля из формы документа в текст договора</p>
							</div>
							<div>
								<UButton
								label="Вставить номер счета"
								icon="i-lucide-file-text"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ НОМЕР_СЧЕТА }}')"
								/>
							</div>
							<div>
								<UButton
								label="Вставить дату"
								icon="i-lucide-calendar"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ ДАТА }}')"
								/>
							</div>
							<div>
								<UButton
								label="Вставить срок оплаты"
								icon="i-lucide-clock"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ СРОК_ОПЛАТЫ }}')"
								/>
							</div>
							<div>
								<UButton
								label="Вставить срок поставки"
								icon="i-lucide-clock"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ СРОК_ПОСТАВКИ }}')"
								/>
							</div>
						</div>
					</UCard>
				</div>

			</div>
		</template>

		<template #footer>
			<div class="flex gap-2">
				<UButton
					icon="i-lucide-x"
					label="Отмена"
					color="neutral"
					variant="subtle"
					@click="closeTemplateEditor()"
				/>
				<UButton
					icon="i-lucide-check"
					label="Сохранить"
					color="primary"
					variant="subtle"
					@click="saveContractTerms()"
				/>
			</div>
		</template>
	</UModal>
</template>
