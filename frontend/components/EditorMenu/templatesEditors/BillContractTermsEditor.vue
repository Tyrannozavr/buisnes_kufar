<script setup lang="ts">
import type { SelectMenuItem } from "@nuxt/ui"
import { Editor } from "~/constants/keys"
import {
	contractTermsSelectValueForTemplate,
	useContractConditionTemplates,
} from "~/composables/useContractConditionTemplates"
import type { ContractConditionTemplateType } from "~/types/contractConditionTemplate"

const isDisabled = useTypedState(Editor.IS_DISABLED)
const templateEditorOpen = ref(false)
const conditionNumber = ref(0)
const billType = useTypedState(Editor.BILL_TYPE)
const route = useRoute()
const toast = useToast()

const dealId = computed(() => Number(route.query.dealId) || null)
const templateType = computed<ContractConditionTemplateType>(() =>
	billType.value?.value === "bill-offer" ? "bill_offer" : "bill_contract",
)

const {
	templates,
	templateItems,
	saveTemplate,
	applyTemplateById,
	applyTextToTypedState,
	refreshTemplates,
} = useContractConditionTemplates(templateType, dealId)

const contractTermsTextContract = useTypedState(Editor.CONTRACT_TERMS_TEXT_CONTRACT)
const contractTermsCheckContract = useTypedState(Editor.CONTRACT_TERMS_CHECK_CONTRACT)
const paymentTermsCheckContract = useTypedState(Editor.PAYMENT_TERMS_CHECK_CONTRACT)
const deliveryTermsCheckContract = useTypedState(Editor.DELIVERY_TERMS_CHECK_CONTRACT)
const paymentTermsContract = useTypedState(Editor.PAYMENT_TERMS_CONTRACT)
const deliveryTermsContract = useTypedState(Editor.DELIVERY_TERMS_CONTRACT)
const contractTermsContract = useTypedState(Editor.CONTRACT_TERMS_CONTRACT)

const contractTermsTextOffer = useTypedState(Editor.CONTRACT_TERMS_TEXT_OFFER)
const contractTermsCheckOffer = useTypedState(Editor.CONTRACT_TERMS_CHECK_OFFER)
const paymentTermsCheckOffer = useTypedState(Editor.PAYMENT_TERMS_CHECK_OFFER)
const paymentTermsOffer = useTypedState(Editor.PAYMENT_TERMS_OFFER)
const contractTermsOffer = useTypedState(Editor.CONTRACT_TERMS_OFFER)

const editorText = ref("")
const selectedTemplate = ref<{ label: string; value: number | "custom" }>({
	label: "Свой шаблон",
	value: "custom",
})
const templateName = ref("")
const isDefault = ref(false)
/** Не реагировать на смену селекта, пока открываем модалку */
const hydratingEditor = ref(false)

const selectItems = computed<SelectMenuItem[]>(() => templateItems.value as SelectMenuItem[])

const isContract = computed(() => billType.value?.value === "bill-contract")
const isOffer = computed(() => billType.value?.value === "bill-offer")

const templateLabel = (name: string, asDefault: boolean) =>
	asDefault ? `${name} (по умолчанию)` : name

const openTemplateEditor = async () => {
	hydratingEditor.value = true
	try {
		await refreshTemplates()
		const list = templates.value ?? []
		const selectValue = isContract.value
			? contractTermsContract.value?.value
			: contractTermsOffer.value?.value
		const currentText = (
			isContract.value
				? contractTermsTextContract.value
				: contractTermsTextOffer.value
		) ?? ""

		// 1) Селект справа «Стандартный, доставка …» → текст из API-шаблона компании
		const matchedBySelect =
			selectValue && selectValue !== "custom"
				? list.find((t) => contractTermsSelectValueForTemplate(t) === selectValue)
				: undefined

		// 2) Иначе точное совпадение с уже сохранённым текстом сделки
		const matchedByContent = currentText.trim()
			? list.find((t) => t.content_text === currentText)
			: undefined

		const matched = matchedBySelect ?? matchedByContent

		if (matched) {
			editorText.value = matched.content_text
			selectedTemplate.value = {
				label: templateLabel(matched.name, matched.is_default),
				value: matched.id,
			}
			templateName.value = matched.name
			isDefault.value = matched.is_default
			// Синхронизируем state: бланк раньше брал hardcoded-константы, editor — пустой state
			if (!currentText.trim() || currentText !== matched.content_text) {
				applyTextToTypedState(matched.content_text)
			}
		} else if (currentText.trim()) {
			editorText.value = currentText
			selectedTemplate.value = { label: "Свой шаблон", value: "custom" }
			templateName.value = ""
			isDefault.value = false
		} else {
			const fallback = list.find((t) => t.is_default) ?? list[0]
			if (fallback) {
				editorText.value = fallback.content_text
				selectedTemplate.value = {
					label: templateLabel(fallback.name, fallback.is_default),
					value: fallback.id,
				}
				templateName.value = fallback.name
				isDefault.value = fallback.is_default
				applyTextToTypedState(fallback.content_text)
			} else {
				editorText.value = ""
				selectedTemplate.value = { label: "Свой шаблон", value: "custom" }
				templateName.value = ""
				isDefault.value = false
			}
		}

		conditionNumber.value = countConditions(editorText.value)
		templateEditorOpen.value = true
	} finally {
		await nextTick()
		hydratingEditor.value = false
	}
}

const closeTemplateEditor = () => {
	templateEditorOpen.value = false
}

const countConditions = (text: string): number => {
	if (!text) return 0
	const conditions = text.match(/^\d+/gm)
	const maxCondition = Math.max(...(conditions?.map((c) => Number(c)) ?? []))
	if (maxCondition === -Infinity) return 0
	return maxCondition
}

const addCondition = () => {
	conditionNumber.value++
	editorText.value += `\n${conditionNumber.value}.\t`
}

const insertField = (field: string) => {
	const textarea = document.getElementById("contract-terms-textarea") as HTMLTextAreaElement | null
	if (!textarea) {
		editorText.value += field
		return
	}
	const start = textarea.selectionStart
	const end = textarea.selectionEnd
	const before = editorText.value.substring(0, start)
	const after = editorText.value.substring(end)
	editorText.value = before + field + after
	nextTick(() => {
		textarea.focus()
		const position = start + field.length
		textarea.setSelectionRange(position, position)
	})
}

const syncTermChecksFromText = (text: string) => {
	const hasPayment = text.includes("{{ СРОК_ОПЛАТЫ }}")
	const hasDelivery = text.includes("{{ СРОК_ПОСТАВКИ }}")

	if (isContract.value) {
		if (hasPayment) {
			paymentTermsCheckContract.value = true
			if (!paymentTermsContract.value) paymentTermsContract.value = "3"
		}
		if (hasDelivery) {
			deliveryTermsCheckContract.value = true
			if (!deliveryTermsContract.value) deliveryTermsContract.value = "10"
		}
	} else if (isOffer.value) {
		if (hasPayment) {
			paymentTermsCheckOffer.value = true
			if (!paymentTermsOffer.value) paymentTermsOffer.value = "3"
		}
	}
}

watch(editorText, (text) => {
	conditionNumber.value = countConditions(text)
	syncTermChecksFromText(text)
})

watch(
	selectedTemplate,
	(selected) => {
		if (hydratingEditor.value || !selected) return
		if (selected.value === "custom") {
			editorText.value = isContract.value
				? contractTermsTextContract.value ?? ""
				: contractTermsTextOffer.value ?? ""
			templateName.value = templateName.value || ""
			isDefault.value = false
			return
		}
		const template = (templates.value ?? []).find((item) => item.id === selected.value)
		if (!template) return
		editorText.value = template.content_text
		templateName.value = template.name
		isDefault.value = template.is_default
		applyTemplateById(template.id)
	},
	{ deep: true },
)

const saveContractTerms = async () => {
	const selectedId = selectedTemplate.value?.value === "custom" ? null : Number(selectedTemplate.value?.value)
	const nameForSave =
		templateName.value.trim() ||
		(selectedId
			? (templates.value ?? []).find((t) => t.id === selectedId)?.name ?? ""
			: "Свой шаблон")

	const saved = await saveTemplate({
		templateId: selectedId && !Number.isNaN(selectedId) ? selectedId : null,
		name: nameForSave,
		contentText: editorText.value,
		isDefault: isDefault.value,
	})

	applyTextToTypedState(editorText.value)
	syncTermChecksFromText(editorText.value)

	if (isContract.value) {
		contractTermsCheckContract.value = Boolean(editorText.value.trim())
	} else {
		contractTermsCheckOffer.value = Boolean(editorText.value.trim())
	}

	if (saved) {
		toast.add({ title: "Шаблон сохранён", color: "success" })
		selectedTemplate.value = {
			label: saved.is_default ? `${saved.name} (по умолчанию)` : saved.name,
			value: saved.id,
		}
		templateName.value = saved.name
		isDefault.value = saved.is_default
	}

	templateEditorOpen.value = false
}
</script>

<template>
	<UModal
		v-if="(contractTermsCheckContract && isContract) || (contractTermsCheckOffer && isOffer)"
		title="Редактор условий договора"
		description="Выберите шаблон или создайте свой. Вставки сроков активируют соответствующие галки."
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
				<div class="w-2/3">
					<textarea
						id="contract-terms-textarea"
						class="w-full h-full bg-gray-100 p-4 rounded-xl resize-none"
						v-model="editorText"
						placeholder="Введите условия договора"
						@keydown.enter.prevent="addCondition()"
					/>
				</div>

				<div class="max-w-1/3 min-w-1/3">
					<UCard class="flex flex-col gap-2 h-full" variant="subtle">
						<div class="flex flex-col gap-2">
							<p class="text-sm text-gray-500">Шаблон условий договора</p>
							<USelectMenu
								placeholder="Выберите шаблон"
								:items="selectItems"
								v-model="selectedTemplate"
								class="w-full"
							/>
							<UInput
								v-model="templateName"
								placeholder="Название шаблона"
								class="w-full"
							/>
							<UCheckbox v-model="isDefault" label="По умолчанию" size="md" />

							<p class="text-sm text-gray-500 mt-2">Вставить поле в курсор</p>
							<UButton
								label="Номер счета"
								icon="i-lucide-file-text"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ НОМЕР_СЧЕТА }}')"
							/>
							<UButton
								label="Дата"
								icon="i-lucide-calendar"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ ДАТА }}')"
							/>
							<UButton
								label="Срок оплаты"
								icon="i-lucide-clock"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ СРОК_ОПЛАТЫ }}')"
							/>
							<UButton
								v-if="isContract"
								label="Срок поставки"
								icon="i-lucide-clock"
								color="neutral"
								variant="subtle"
								@click.prevent="insertField('{{ СРОК_ПОСТАВКИ }}')"
							/>
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
