<script setup lang="ts">
import type { SelectMenuItem } from "@nuxt/ui"
import { Editor } from "~/constants/keys"

const isDisabled = useTypedState(Editor.IS_DISABLED)
const templateEditorOpen = ref(false)
const conditionNumber = ref(0)
const billType = useTypedState(Editor.BILL_TYPE)

const contractTermsTextContract = useTypedState(Editor.CONTRACT_TERMS_TEXT_CONTRACT)
const contractTermsCheckContract = useTypedState(Editor.CONTRACT_TERMS_CHECK_CONTRACT)
const customContractTermsTextContract = ref("")
const selectedContractTermsContract = ref<{ label: string, value: string }>({ label: "Свой шаблон", value: "custom" })
const contractTermsOptionsContract = ref<SelectMenuItem[]>([
	{ label: "Стандартный", value: "standard" },
	{ label: "Новый шаблон", value: "new-template" },
	{ label: "Свой шаблон", value: "custom" },
])

const contractTermsTextOffer = useTypedState(Editor.CONTRACT_TERMS_TEXT_OFFER)
const contractTermsCheckOffer = useTypedState(Editor.CONTRACT_TERMS_CHECK_OFFER)
const customContractTermsTextOffer = ref("")
const selectedContractTermsOffer = ref<{ label: string, value: string }>({ label: "Свой шаблон", value: "custom" })
const contractTermsOptionsOffer = ref<SelectMenuItem[]>([
	{ label: "Стандартный", value: "standard" },
	{ label: "Новый шаблон", value: "new-template" },
	{ label: "Свой шаблон", value: "custom" },
])

const openTemplateEditor = () => {
	templateEditorOpen.value = true
}

const closeTemplateEditor = () => {
	templateEditorOpen.value = false
	if (billType.value.value === 'bill-contract') {
		customContractTermsTextContract.value = ''
	} else if (billType.value.value === 'bill-offer') {
		customContractTermsTextOffer.value = ''
	}
}

const saveContractTerms = () => {
	if (billType.value.value === 'bill-contract') {
		contractTermsTextContract.value = customContractTermsTextContract.value
	} else if (billType.value.value === 'bill-offer') {
		contractTermsTextOffer.value = customContractTermsTextOffer.value
	}
	templateEditorOpen.value = false
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
	if (billType.value.value === 'bill-contract') {
		customContractTermsTextContract.value += `\n${conditionNumber.value}.\t`
	} else if (billType.value.value === 'bill-offer') {
		customContractTermsTextOffer.value += `\n${conditionNumber.value}.\t`
	}
}

const insertField = ( field: string) => {
	const textarea = document.getElementById('textarea') as HTMLTextAreaElement

	const start = textarea.selectionStart
	const end = textarea.selectionEnd
	const before = textarea.value.substring(0, start)
	const after = textarea.value.substring(end)
	if (billType.value.value === 'bill-contract') {
		customContractTermsTextContract.value = before + field + after
	} else if (billType.value.value === 'bill-offer') {
		customContractTermsTextOffer.value = before + field + after
	}

	nextTick(() => {
		textarea.focus()
		const position = start + field.length
		textarea.setSelectionRange(position, position)
	})
}

//подсчет пунктов текста
watch(() => [customContractTermsTextContract.value, customContractTermsTextOffer.value], () => {
	if (billType.value.value === 'bill-contract') {
		conditionNumber.value = countConditions(customContractTermsTextContract.value)
	} else if (billType.value.value === 'bill-offer') {
		conditionNumber.value = countConditions(customContractTermsTextOffer.value)
	}
}, { deep: true })

//вставка шаблона для редактирования
watch(() => [selectedContractTermsContract, selectedContractTermsOffer],
	() => {
		if (billType.value.value === 'bill-contract') {
			if (selectedContractTermsContract.value.value === 'standard') {
				customContractTermsTextContract.value = `Основные условия настоящего договора-счета № {{ НОМЕР_СЧЕТА }} от {{ ДАТА }}
1. 	Предметом настоящего Счета-договора является поставка товарно-материальных ценностей (далее - "товар").
2. 	Оплата настоящего Счета-договора означает согласие Покупателя с условиями оплаты и поставки товара.	
3. 	Настоящий Счет-договор действителен в течение {{ СРОК_ОПЛАТЫ }} рабочих дней от даты его составления включительно. При отсутствии оплаты в указанный срок настоящий Счет-договор признается недействительным.
4. 	Поставщик обязан доставить оплаченный товар и передать его Покупателю в течение {{ СРОК_ПОСТАВКИ }} рабочих дней с момента зачисления оплаты на расчетный счет
5. 	Оплаченный товар доставляется Покупателю силами ПОСТАВЩИКА/ПОКУПАТЕЛЯ
6. 	Оплата Счета-договора третьими лицами (сторонами), а также неполная (частичная) оплата Счета-договора не допускается. Покупатель не имеет права производить выборочную оплату позиций счета и требовать поставку товара по выбранным позициям.
7. 	Поставщик вправе не выполнять поставку товара до зачисления оплаты на расчетный счет.
8. 	Покупатель обязан принять оплаченный товар лично или через уполномоченного представителя. Передача товара осуществляется при предъявлении документа, удостоверяющего личность, и/или доверенности оформленной в установленном порядке.
9. 	Подписание Покупателем или его уполномоченным представителем товарной накладной означает согласие Покупателя с комплектностью и надлежащим качеством товара.`

			} else if (selectedContractTermsContract.value.value === 'new-template') {
				customContractTermsTextContract.value = 'Введите условия договора'
			} else if (selectedContractTermsContract.value.value === 'custom') {
				customContractTermsTextContract.value = contractTermsTextContract.value
			}
		} else if (billType.value.value === 'bill-offer') {
			if (selectedContractTermsOffer.value.value === 'standard') {
				customContractTermsTextOffer.value = `1.	Предметом настоящего счета-оферты является поставка товара по перечню изделий поставщиком покупателю.
2.	Подписывая настоящий счет-оферту, Покупатель дает согласие на то, что товар надлежащего качества обмену и возврату не подлежит.
3.	Осмотр товара Покупателем происходит при получении. Покупатель проводит обследование единиц продукции на предмет отсутствия брака и дефектов, проверяет комплектность партии. При обнаружении недочетов Покупателем составляется акт. При отсутствии акта Поставщик претензии не принимает.
4.	Покупатель обязуется оплатить товар на условиях 100% предоплаты в сумме, указанной в счете, в течение {{ СРОК_ОПЛАТЫ }} рабочих дней по указанным реквизитам.
5.	Оплаченный товар доставляется Покупателю силами ПОСТАВЩИКА/ПОКУПАТЕЛЯ со склада Поставщика, расположенного по адресу: {{ АДРЕС_ПРОИЗВОДСТВА_ПОСТАВЩИКА}}.
6.	После получения товара Покупатель обязан подписать Товарную накладную.
`
			} else if (selectedContractTermsOffer.value.value === 'new-template') {
				customContractTermsTextOffer.value = 'Введите условия договора'
			} else if (selectedContractTermsOffer.value.value === 'custom') {
				customContractTermsTextOffer.value = contractTermsTextOffer.value
			} 
		}
}, { deep: true, immediate: true })
</script>

<template>
	<UModal
		v-if="(contractTermsCheckContract && billType.value === 'bill-contract') || (contractTermsCheckOffer && billType.value === 'bill-offer')"
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
						v-if="billType.value === 'bill-contract'"
						id="textarea"
						class="w-full h-full bg-gray-100 p-4 rounded-xl resize-none"
						v-model="customContractTermsTextContract"
						placeholder="Введите условия договора"
						@keydown.enter.prevent="addCondition()"
					/>
					<textarea
						v-if="billType.value === 'bill-offer'"
						id="textarea"
						class="w-full h-full bg-gray-100 p-4 rounded-xl resize-none"
						v-model="customContractTermsTextOffer"
						placeholder="Введите условия договора"
						@keydown.enter.prevent="addCondition()"
					/>
				</div>

				<!-- Меню для счета-договора -->
				<div v-if="billType.value === 'bill-contract'" class="max-w-1/3 min-w-1/3">
					<UCard class="flex flex-col gap-2 h-full" variant="subtle">
						<div class="flex flex-col gap-2">
							<div>
								<p class="text-sm text-gray-500">Выберите шаблон, на основании которого будут сгенерированы условия договора</p>
							</div>
							<div>
								<USelectMenu
									placeholder="Выберите шаблон"
									:items="contractTermsOptionsContract"
									v-model="selectedContractTermsContract"
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
								@click.prevent="insertField('{{ СРОК_ОПЛАТЫ_СЧЕТА_ДОГОВОРА }}')"
								/>
							</div>
							<div>
								<UButton
								label="Вставить срок поставки"
								icon="i-lucide-clock"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ СРОК_ПОСТАВКИ_СЧЕТА_ДОГОВОРА }}')"
								/>
							</div>
						</div>
					</UCard>
				</div>

				<!-- Меню для счета-оферты -->
				 <div v-if="billType.value === 'bill-offer'" class="max-w-1/3 min-w-1/3">
					<UCard class="flex flex-col gap-2 h-full" variant="subtle">
						<div class="flex flex-col gap-2">
							<div>
								<p class="text-sm text-gray-500">Выберите шаблон, на основании которого будут сгенерированы условия договора</p>
							</div>
							<div>
								<USelectMenu
									placeholder="Выберите шаблон"
									:items="contractTermsOptionsOffer"
									v-model="selectedContractTermsOffer"
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
								@click.prevent="insertField('{{ СРОК_ОПЛАТЫ_СЧЕТА_ОФЕРТА }}')"
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
