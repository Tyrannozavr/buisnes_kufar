<script setup lang="ts">
import { ListItem } from "@tiptap/extension-list"
import { TextStyleKit } from "@tiptap/extension-text-style"
import { Editor as TiptapEditor, EditorContent } from "@tiptap/vue-3"
import { Mark, mergeAttributes } from "@tiptap/core"
import StarterKit from "@tiptap/starter-kit"
import { TextAlign } from "@tiptap/extension-text-align"
import { TableKit } from "@tiptap/extension-table"
import type { DropdownMenuItem } from "@nuxt/ui"
import mammoth from "mammoth"
import { Editor, TemplateElement } from "~/constants/keys"
import { useSupplyContractTemplates } from "~/composables/useSupplyContractTemplates"
import type { SupplyContractTemplateType } from "~/types/supplyContractTemplate"
import {
	createSupplyContractFieldTokenHtml,
	getSupplyContractFieldLabel,
	renderSupplyContractFields,
	SUPPLY_CONTRACT_FIELD_ATTRIBUTE,
	SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE,
	supplyContractFieldDefinitions,
	supplyContractTermFieldDefinitions,
	type SupplyContractParty,
} from "~/utils/supplyContractFields"

const { label, templateType } = defineProps<{
	label: string
	templateType: SupplyContractTemplateType
}>()

const selectedTemplateId = defineModel<number | undefined>("selectedTemplateId")

const emit = defineEmits<{
	saved: [templateId: number]
}>()

const route = useRoute()
const dealId = computed(() => Number(route.query.dealId) || null)
const toast = useToast()
const { editSupplyContractText, editSupplyContractSpecificationText, findDeal } = useDeals()

const templateTypeRef = computed(() => templateType)
const {
	templates,
	templateItems,
	saveTemplate,
} = useSupplyContractTemplates(templateTypeRef, dealId)

const templateEditorOpen = ref(false)
const templateName = ref("")
const isDefault = ref(false)
const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
const specificationHTML = useTypedState(TemplateElement.SPECIFICATION)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const supplyContractOfficialsSeller = useTypedState(Editor.SUPPLY_CONTRACT_OFFICIALS_SELLER, () => ref([]))
const fileInput = ref<HTMLInputElement | null>(null)
const currentDeal = computed(() => dealId.value ? findDeal(dealId.value) : undefined)

const supplyContractTableData = useTypedState(Editor.SUPPLY_CONTRACT_TABLE_DATA)
const tableProducts = supplyContractTableData.value?.products
const amount = supplyContractTableData.value?.amount
const amountExclVat = supplyContractTableData.value?.amountExclVat
const amountVatRate = supplyContractTableData.value?.amountVatRate

const DEFAULT_FONT_SIZE = "14px"
const fontSize = ref<string>(DEFAULT_FONT_SIZE)
const fontSizeItems = [
	{ label: '10', value: '10px' },
	{ label: '12', value: '12px' },
	{ label: '14', value: '14px' },
	{ label: '16', value: '16px' },
	{ label: '18', value: '18px' },
	{ label: '20', value: '20px' },
	{ label: '22', value: '22px' },
	{ label: '24', value: '24px' },
	{ label: '26', value: '26px' },
	{ label: '28', value: '28px' },
	{ label: '30', value: '30px' },
	{ label: '32', value: '32px' },
	{ label: '34', value: '34px' },
	{ label: '36', value: '36px' }
]

const supplyContractParties: SupplyContractParty[] = ["seller", "buyer"]

const getSupplyContractFieldContext = () => ({
	seller: currentDeal.value?.seller,
	buyer: currentDeal.value?.buyer,
	sellerOfficial: supplyContractOfficialsSeller.value?.[0],
	paymentTerms: currentDeal.value?.bill.paymentTermsContract,
	deliveryTerms: currentDeal.value?.bill.deliveryTermsContract,
})

const insertSupplyContractField = (party: SupplyContractParty, fieldKey: typeof supplyContractFieldDefinitions[number]["key"]) => {
	editor
		.chain()
		.focus()
		.insertContent(createSupplyContractFieldTokenHtml(party, fieldKey, getSupplyContractFieldContext()))
		.run()
}

const insertSupplyContractTermField = (fieldKey: typeof supplyContractTermFieldDefinitions[number]["key"]) => {
	editor
		.chain()
		.focus()
		.insertContent(createSupplyContractFieldTokenHtml("contract", fieldKey, getSupplyContractFieldContext()))
		.run()
}

const getTemplateHtml = () =>
	templateType === 'supply_contract' ? supplyContractHTML.value : specificationHTML.value

const getRenderedTemplateHtml = () =>
	renderSupplyContractFields(getTemplateHtml(), getSupplyContractFieldContext())

const paymentTermsItems: DropdownMenuItem[] = supplyContractTermFieldDefinitions.map((field) => ({
	label: field.label,
	onClick: () => insertSupplyContractTermField(field.key),
}))

const requisitesItems: DropdownMenuItem[] = supplyContractParties.flatMap((party) =>
	supplyContractFieldDefinitions.map((field) => ({
		label: getSupplyContractFieldLabel(party, field.key),
		onClick: () => insertSupplyContractField(party, field.key),
	})),
)

const scrollableDropdownMenuUi = {
	content: 'max-h-72',
}

const SupplyContractFieldMark = Mark.create({
	name: "supplyContractField",
	priority: 1000,
	inclusive: false,

	addAttributes() {
		return {
			[SUPPLY_CONTRACT_FIELD_ATTRIBUTE]: {
				default: null,
				parseHTML: (element) => element.getAttribute(SUPPLY_CONTRACT_FIELD_ATTRIBUTE),
				renderHTML: (attributes) => {
					const value = attributes[SUPPLY_CONTRACT_FIELD_ATTRIBUTE]
					return value ? { [SUPPLY_CONTRACT_FIELD_ATTRIBUTE]: value } : {}
				},
			},
			[SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE]: {
				default: null,
				parseHTML: (element) => element.getAttribute(SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE),
				renderHTML: (attributes) => {
					const value = attributes[SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE]
					return value ? { [SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE]: value } : {}
				},
			},
		}
	},

	parseHTML() {
		return [{ tag: `span[${SUPPLY_CONTRACT_FIELD_ATTRIBUTE}]` }]
	},

	renderHTML({ HTMLAttributes }) {
		return ["span", mergeAttributes(HTMLAttributes), 0]
	},
})

//добавить проверку для клиента
const editor = new TiptapEditor({
	content: getRenderedTemplateHtml(),
	extensions: [
		StarterKit,
		TextStyleKit,
		SupplyContractFieldMark,
		ListItem.configure({ HTMLAttributes: { class: "list-item" } }),
		TextAlign.configure({ types: ["heading", "paragraph"] }),
		TableKit.configure({
			table: {
				resizable: false,
				renderWrapper: true,
				HTMLAttributes: {
					class: "my_table p-5 mb-5 w-[99%]"
				}
			},
			tableCell: {
				HTMLAttributes: {
					class: "border text-left"
				}
			},
			tableHeader: {
				HTMLAttributes: {
					class: "border text-bold text-center"
				}
			}
		})
	],
	injectCSS: false,
	autofocus: "start"
})

// преобразование документа в HTML и вставка в редактор
const handleFileSelect = async (e: Event) => {
	const file = (e.target as HTMLInputElement).files?.[0]
	if (file) {
		const arrayBuffer = await file.arrayBuffer()
		const result = await mammoth.convertToHtml({ arrayBuffer })
		editor.chain().focus().insertContent(result.value).run()
	}
}

// синхронизация размера шрифта из выделения текста
const syncFontSizeFromSelection = () => {
	const attrs = editor.getAttributes("textStyle") as { fontSize?: string | null }
	const size = attrs.fontSize
	fontSize.value = size && size.length > 0 ? size : DEFAULT_FONT_SIZE
}

// выбор размера шрифта
const handleFontSizeSelect = (value: string) => {
	editor.chain().focus().setFontSize(value).run()
}

const handleTemplateSelect = (templateId: number | undefined) => {
	selectedTemplateId.value = templateId

	const selected = (templates.value ?? []).find((item) => item.id === templateId)
	if (!selected) return

	templateName.value = selected.name
	isDefault.value = selected.is_default
	editor.commands.setContent(renderSupplyContractFields(selected.content_html, getSupplyContractFieldContext()))
}

const handleCreateNewTemplate = () => {
	selectedTemplateId.value = undefined
	templateName.value = ''
	isDefault.value = false
	editor.commands.clearContent()
}

// открытие редактора договора поставки
const openTemplateEditor = () => {
	const selected = (templates.value ?? []).find((item) => item.id === selectedTemplateId.value)
	templateName.value = selected?.name ?? ""
	isDefault.value = selected?.is_default ?? false
	editor.commands.setContent(getRenderedTemplateHtml())
	templateEditorOpen.value = true
}

// сохранение шаблона в БД и HTML в превью сделки
const saveSupplyContract = async () => {
	const contentHtml = editor.getHTML()

	if (templateType === 'supply_contract') {
		supplyContractHTML.value = contentHtml
	} else {
		specificationHTML.value = contentHtml
	}

	const saved = await saveTemplate({
		templateId: selectedTemplateId.value,
		name: templateName.value,
		contentHtml,
		isDefault: isDefault.value,
	})

	if (!saved) return

	selectedTemplateId.value = saved.id
	if (dealId.value && route.query.role === 'seller') {
		if (templateType === 'supply_contract') {
			editSupplyContractText(dealId.value, contentHtml)
		} else {
			editSupplyContractSpecificationText(dealId.value, contentHtml)
		}
	}
	templateEditorOpen.value = false
	toast.add({ title: 'Шаблон сохранён', color: 'success' })
	emit('saved', saved.id)
}

//в следующих трех функциях не вставлять пробелы и табуляции в сроках с таблицами (особенности работы библиотеки Tiptap)
const tableBody = () => {
	const body = tableProducts.map((item: any, index: number) =>
		`<tr><td><p>${index + 1}</p></td>
		<td><p>${item.name}</p></td>
		<td><p>${item.article}</p></td>
		<td><p>${item.quantity}</p></td>
		<td><p>${item.units}</p></td>
		<td><p>${item.price}</p></td>
		<td><p>${item.amount}</p></td>
		</tr>`).join('')
	return body
}

const tableFooter = () => {
	const footer =
		`<tr>
		<td colspan="6"><p style="text-align: right;margin-right: 30px;">Итого:</p></td>
		<td><p style="text-align: right">${ amountExclVat }</p></td></tr>
		<tr>
		<td colspan="6"><p style="text-align: right;margin-right: 30px;">НДС 20%:</p></td>
		<td><p style="text-align: right">${ amountVatRate }</p></td></tr>
		<tr>
		<td colspan="6"><p style="text-align: right;margin-right: 30px;">Итого с НДС:</p></td>
		<td><p style="text-align: right">${ amount }</p></td>
		</tr>`.trim()
	return footer
}

const insertTable = () => {
	const tableHeader =
`<tr>
<th><p>№</p></th>
<th><p>Название</p></th>
<th><p>Артикул</p></th>
<th><p>Кол-во</p></th>
<th><p>Ед. изм.</p></th>
<th><p>Цена</p></th>
<th><p>Сумма</p></th>
</tr>`
	const table = `<table>${tableHeader}${tableBody()}${tableFooter()}</table>`
	return table
}


//подписка на изменения редактора
onMounted(() => {
	editor.on("selectionUpdate", syncFontSizeFromSelection)
	editor.on("transaction", syncFontSizeFromSelection)
	nextTick(() => syncFontSizeFromSelection())
})

// отписка от изменений редактора
onBeforeUnmount(() => {
	editor.off("selectionUpdate", syncFontSizeFromSelection)
	editor.off("transaction", syncFontSizeFromSelection)
	editor.destroy()
})
</script>

<template>
	<UModal
		:title="label"
		v-model:open="templateEditorOpen"
		:dismissible="false"
		:ui="{
			content: 'max-w-5xl h-full',
			footer: 'justify-end'
		}"
	>
		<UButton
			:disabled="isDisabled"
			:label="label"
			color="neutral"
			variant="ghost"
			@click="openTemplateEditor()"
			class="flex w-full justify-end hover:cursor-pointer hover:bg-gray-50"
		/>
		<template #header>
			<div class="flex flex-col gap-3 w-full">
				<div class="flex gap-2">
					<USelect
						class=""
						:items="templateItems"
						:model-value="selectedTemplateId"
						placeholder="Выберите шаблон для редактирования"
						size="lg"
						@update:model-value="handleTemplateSelect"
					/>
					<UButton
						class=" justify-center"
						icon="i-lucide-file-plus"
						label="Создать новый шаблон"
						color="neutral"
						variant="subtle"
						@click="handleCreateNewTemplate"
					/>
				</div>

				<div class="flex justify-between">
					<div class="flex gap-2 w-4/5">
						<UInput
							class="w-1/3"
							placeholder="Название шаблона"
							size="lg"
							v-model="templateName"
						/>
						<UCheckbox
							size="lg"
							class="w-2/3 self-center"
							label="Использовать по умолчанию"
							v-model="isDefault"
						/>
					</div>

					<div class="self-center">
						<UButton
							icon="i-lucide-check"
							label="Сохранить"
							color="primary"
							variant="subtle"
							@click="saveSupplyContract()"
							/>
						</div>
					</div>
					
				<UCard
					class="flex w-full"
					variant="subtle"
					:ui="{ body: 'bg-[rgb(68,114,196)] w-full p-3 sm:p-3'}"
				>
					<div class="flex gap-2 flex-wrap justify-between">

						<!-- Выбора папки с текстом и очистки форматирования -->
						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UButton
								type="button"
								icon="i-lucide-folder-open"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Выберите документ(.docx, .doc) с текстом для вставки в редактор"
								@click="fileInput?.click()"
							/>
							<input
								ref="fileInput"
								class="hidden"
								aria-hidden="true"
								type="file"
								accept=".docx, .doc"
								@change="handleFileSelect"
							/>
							<UButton
								@click="editor.chain().focus().unsetAllMarks().run()"
								:disabled="!editor.can().chain().focus().unsetAllMarks().run()"
								icon="i-lucide-brush-cleaning"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Очистить форматирование"
							/>
						</div>

						<!-- Отмена и повтор действия -->
						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UButton
								@click="editor.chain().focus().undo().run()"
								:disabled="!editor.can().chain().focus().undo().run()"
								icon="i-lucide-undo"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
							/>
							<UButton
								@click="editor.chain().focus().redo().run()"
								:disabled="!editor.can().chain().focus().redo().run()"
								icon="i-lucide-redo"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
							/>
						</div>

						<!-- Выбора размера шрифта -->
						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<USelect
								@update:model-value="handleFontSizeSelect"
								:items="fontSizeItems"
								v-model="fontSize"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300 w-16"
								title="Размер шрифта"
							/>
						</div>

						<!-- Выбора жирности, курсива, подчеркивания -->
						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UButton
								@click="editor.chain().focus().toggleBold().run()"
								:disabled="!editor.can().chain().focus().toggleBold().run()"
								:class="editor.isActive('bold') ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-bold"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Жирный текст"
							/>
							<UButton
								@click="editor.chain().focus().toggleItalic().run()"
								:disabled="!editor.can().chain().focus().toggleItalic().run()"
								:class="editor.isActive('italic') ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-italic"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Курсивный текст"
							/>
							<UButton
								@click="editor.chain().focus().toggleUnderline().run()"
								:disabled="!editor.can().chain().focus().toggleUnderline().run()"
								:class="editor.isActive('underline') ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-underline"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Подчеркнутый текст"
							/>
						</div>

						<!-- Выравнивание текста -->
						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UButton
								@click="editor.chain().focus().setTextAlign('left').run()"
								:class="editor.isActive({ textAlign: 'left' }) ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-align-left"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Выравнивание по левому краю"
							/>
							<UButton
								@click="editor.chain().focus().setTextAlign('center').run()"
								:class="editor.isActive({ textAlign: 'center' }) ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-align-center"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Выравнивание по центру"
							/>
							<UButton
								@click="editor.chain().focus().setTextAlign('right').run()"
								:class="editor.isActive({ textAlign: 'right' }) ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-align-right"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Выравнивание по правому краю"
							/>
							<UButton
								@click="editor.chain().focus().setTextAlign('justify').run()"
								:class="editor.isActive({ textAlign: 'justify' }) ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-align-justify"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Выравнивание по ширине"
							/>
						</div>

						<!-- Выбор списка и нумерованного списка -->
						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UButton
								@click="editor.chain().focus().toggleBulletList().run()"
								:class="editor.isActive('bulletList') ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-list"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Список"
							/>
							<UButton
								@click="editor.chain().focus().toggleOrderedList().run()"
								:class="editor.isActive('orderedList') ? 'bg-[rgba(68,115,196,0.7)]' : ''"
								icon="i-lucide-list-ordered"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Нумерованный список"
							/>
						</div>

						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UButton
								@click="editor.chain().focus().insertContent(insertTable()).run()"
								icon="i-lucide-table"
								color="neutral"
								variant="ghost"
								class="hover:bg-gray-300"
								title="Таблица с товарами"
							/>
						</div>

						<div class="flex gap-1 p-1 bg-gray-50 rounded-md">
							<UDropdownMenu :items="paymentTermsItems">
								<UButton
									label="Сроки"
									icon="i-lucide-calendar"
									color="neutral"
									variant="ghost"
									class="hover:bg-gray-300"
									title="Сроки оплаты, поставки и т.д."
								/>
							</UDropdownMenu>

							<UDropdownMenu :items="requisitesItems" :ui="scrollableDropdownMenuUi">
								<UButton
									label="Реквизиты"
									icon="i-lucide-file-text"
									color="neutral"
									variant="ghost"
									class="hover:bg-gray-300"
									title="«ОРГН», «ИНН», «КПП» и т.д."
								/>
							</UDropdownMenu>
						</div>

					</div>
				</UCard>
			</div>
		</template>

		<template #body>
			<div v-if="editor" class="container">
				<editor-content :editor="editor"/>
			</div>
		</template>
	</UModal>
</template>

<style lang="css">
/* Basic editor styles */
.tiptap {
	padding: 10px;
	border: 1px solid #ccc;
	border-radius: 5px;
	min-height: 27rem;
}

.tiptap :first-child {
	margin-top: 0;
}

/* List styles */
.tiptap ul,
.tiptap ol {
	padding: 0 1rem;
	margin: 1.25rem 1rem 1.25rem 0.4rem;
}

.tiptap ul {
	list-style-type: disc;
}

.tiptap ol {
	list-style-type: decimal;
}

.tiptap ul li p,
.tiptap ol li p {
	margin-top: 0.25em;
	margin-bottom: 0.25em;
}

/* Heading styles */
.tiptap h1,
.tiptap h2,
.tiptap h3,
.tiptap h4,
.tiptap h5,
.tiptap h6 {
	line-height: 1.1;
	margin-top: 2.5rem;
	text-wrap: pretty;
}

.tiptap h1,
.tiptap h2 {
	margin-top: 3.5rem;
	margin-bottom: 1.5rem;
}

.tiptap h1 {
	font-size: 1.4rem;
}

.tiptap h2 {
	font-size: 1.2rem;
}

.tiptap h3 {
	font-size: 1.1rem;
}

.tiptap h4,
.tiptap h5,
.tiptap h6 {
	font-size: 1rem;
}

/* Code and preformatted text styles */
.tiptap code {
	background-color: var(--purple-light);
	border-radius: 0.4rem;
	color: var(--black);
	font-size: 0.85rem;
	padding: 0.25em 0.3em;
}

.tiptap pre {
	background: var(--black);
	border-radius: 0.5rem;
	color: var(--white);
	font-family: "JetBrainsMono", monospace;
	margin: 1.5rem 0;
	padding: 0.75rem 1rem;
}

.tiptap pre code {
	background: none;
	color: inherit;
	font-size: 0.8rem;
	padding: 0;
}

.tiptap blockquote {
	border-left: 3px solid var(--gray-3);
	margin: 1.5rem 0;
	padding-left: 1rem;
}

.tiptap hr {
	border: none;
	border-top: 1px solid var(--gray-2);
	margin: 2rem 0;
}

.my_table tr:nth-last-child(-n+3) td {
	border: none;
}

.my_table tr td:nth-child(1) {
	text-align: center;
	width: 5%;
}

.my_table tr td:nth-child(2) {
	width: 35%;
}

.my_table tr td:nth-child(3) {
	text-align: center;
	width: 12%;
}

.my_table tr td:nth-child(4) {
	text-align: center;
	width: 8%;
}

.my_table tr td:nth-child(5) {
	text-align: center;
	width: 10%;
}

.my_table tr td:nth-child(6) {
	text-align: right;
	width: 15%;
}

.my_table tr td:nth-child(7) {
	text-align: right;
	width: 15%;
}
</style>
