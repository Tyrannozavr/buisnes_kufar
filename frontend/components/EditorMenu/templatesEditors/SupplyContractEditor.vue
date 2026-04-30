<script setup lang="ts">
/*
TODO:
- [ ] Добавить логику присвоения данного шаблона флага "шаблон по умолчанию" для дальнейшего использования в других заказах
- [ ] Добавить логику сохранения договора поставки
- [ ] добавить получение пропсов из компонента SupplyContractMenu.vue
- [ ] Дополнить логику вставки таблицы с товарами(добавить реальные данные из заказа)
- [ ] Дополнить логику выбора сроков и реквизитов
*/
import { Editor } from "~/constants/keys"
import { ListItem } from "@tiptap/extension-list"
import { TextStyleKit } from "@tiptap/extension-text-style"
import { Editor as TiptapEditor, EditorContent } from "@tiptap/vue-3"
import StarterKit from "@tiptap/starter-kit"
import { TextAlign } from "@tiptap/extension-text-align"
import { TableKit } from "@tiptap/extension-table"
import type { DropdownMenuItem } from "@nuxt/ui"
import mammoth from "mammoth"
import { TemplateElement } from "~/constants/keys"

const templateEditorOpen = ref(false)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)

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

const paymentTermsItems: DropdownMenuItem[] = [
	{
		label: 'Срок оплаты',
		onClick: () => editor.chain().focus().insertContent('одна ночь').run()
	},
	{
		label: 'Срок поставки',
		onClick: () => editor.chain().focus().insertContent('одна неделя').run()
	}
]
const requisitesItems: DropdownMenuItem[] = [
	{
		label: 'ОРГН',
		onClick: () => editor.chain().focus().insertContent('ОРГН').run()
	},
	{
		label: 'ИНН',
		onClick: () => editor.chain().focus().insertContent('ИНН').run()
	}
]

const fileInput = ref<HTMLInputElement | null>(null)


// Mock объект для billData, чтобы таблица с ним работала корректно
const Data = ref({
  products: [
    {
      name: "Товар 1",
      article: "A001",
      quantity: 10,
      units: "шт",
      price: 500,
      amount: 5000,
    },
    {
      name: "Товар 2",
      article: "B002",
      quantity: 5,
      units: "кг",
      price: 800,
      amount: 4000,
    },
  ],
})

//добавить проверку для клиента
const editor = new TiptapEditor({
	content: `<p>Заполните условия договора поставки</p>`,
	extensions: [
		StarterKit,
		TextStyleKit,
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

// открытие редактора договора поставки
const openTemplateEditor = () => {
	templateEditorOpen.value = true
}

// FIXME: логика присвоения данного шаблона флага "шаблон по умолчанию" для дальнейшего использования в других заказах
const useDefaultTemplate = () => {
	editor.chain().focus().setContent(`<p>Заполните условия договора поставки</p>${"<p></p>".repeat(15)}`).run()
}

// сохранение договора поставки
const saveSupplyContract = () => {
	templateEditorOpen.value = false
	supplyContractHTML.value = editor.getHTML()
}

//в следующих трех функциях не вставлять пробелы и табуляции в сроках с таблицами (особенности работы библиотеки Tiptap)
const tableBody = (data: any) => {
	const body = data.products.map((item: any, index: number) =>
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

const tableFooter = (data: any) => {
	const footer =
		`<tr>
		<td colspan="6"><p style="text-align: right;margin-right: 30px;">Итого:</p></td>
		<td><p style="text-align: right">${data.products.reduce((acc: number, item: any) => acc + item.amount, 0)}</p></td></tr>
		<tr>
		<td colspan="6"><p style="text-align: right;margin-right: 30px;">НДС 20%:</p></td>
		<td><p style="text-align: right">${data.products.reduce((acc: number, item: any) => acc + item.amount * 0.2, 0)}</p></td></tr>
		<tr>
		<td colspan="6"><p style="text-align: right;margin-right: 30px;">Итого с НДС:</p></td>
		<td><p style="text-align: right">${data.products.reduce((acc: number, item: any) => acc + item.amount * 1.2, 0)}</p></td>
		</tr>`.trim()
	return footer
}

const insertTable = (data: any) => {
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
	const table = `<table>${tableHeader}${tableBody(data)}${tableFooter(data)}</table>`
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
		<template #header>
			<div class="flex flex-col gap-3 w-full">
				<div class="flex justify-between">
					<div class="flex gap-2 w-4/5">
						<USelect class="w-1/3" placeholder="Название шаблона" size="xl"/>
						<UCheckbox
							size="xl"
							class="w-2/3 self-center"
							label="Использовать по умолчанию"
							@click="useDefaultTemplate()"
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
					class="flex w-full mb-3"
					variant="subtle"
					:ui="{ body: 'p-0 bg-[rgb(68,114,196)] w-full' }"
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
								@click="editor.chain().focus().insertContent(insertTable(Data)).run()"
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
							
							<UDropdownMenu :items="requisitesItems">
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
