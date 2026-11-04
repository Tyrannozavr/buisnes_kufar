<script setup lang="ts">
import { Editor as TiptapEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { TextAlign } from '@tiptap/extension-text-align'
import { useCarriageContractBlank } from '~/composables/useCarriageContractBlank'
import { DEFAULT_CARRIAGE_CONTRACT_BODY } from '~/utils/carriageContractDefaults'

/**
 * Правое меню вкладки «Договор» для договора перевозки (§2.2).
 * Без «Таблица» и «СпецСим2» — типовой договор.
 */
const {
	documentId,
	bodyHtml,
	customerDetailsCheck,
	carrierDetailsCheck,
	isDisabled,
	loading,
	saving,
	dealId,
	currentDeal,
	fillFromLk,
	applyDefaultBody,
	bumpSlot,
} = useCarriageContractBlank()

const route = useRoute()
const router = useRouter()
const templateEditorOpen = ref(false)
const editor = shallowRef<TiptapEditor | null>(null)

/** Заявки-приложения к этому договору (из снимка сделки). */
const childApplications = computed(() => {
	const parentId = documentId.value
	if (!parentId) return []
	const docs = currentDeal.value?.transportContract?.documents ?? []
	return docs
		.filter(
			(d) =>
				d.type === 'carriage_application' &&
				d.id &&
				(d.parent_id == null || Number(d.parent_id) === parentId),
		)
		.map((d) => ({
			id: Number(d.id),
			number: String(d.number || ''),
			date: d.date ? String(d.date).slice(0, 10) : '',
		}))
		.sort((a, b) => Number(a.number) - Number(b.number))
})

const openApplication = (app: { id: number }) => {
	if (!dealId.value || !app.id) return
	const role = String(route.query.role || 'seller')
	void router.push({
		path: '/profile/editor',
		query: {
			dealId: String(dealId.value),
			role,
			transportDocType: 'carriage_application',
			transportDocId: String(app.id),
		},
		hash: '#contract',
	})
}

const fillFromLkDisabledReason = computed(() => {
	if (!documentId.value) return 'Документ перевозки не выбран'
	if (isDisabled.value) return 'Сначала нажмите «Редактировать»'
	if (loading.value) return 'Идёт загрузка…'
	return ''
})

const templateEditorDisabledReason = computed(() => {
	if (!documentId.value) return 'Документ перевозки не выбран'
	if (isDisabled.value) return 'Сначала нажмите «Редактировать»'
	return ''
})

const ensureEditor = () => {
	if (editor.value || !import.meta.client) return
	editor.value = new TiptapEditor({
		extensions: [
			StarterKit,
			TextAlign.configure({ types: ['heading', 'paragraph'] }),
		],
		content: bodyHtml.value || DEFAULT_CARRIAGE_CONTRACT_BODY,
		editable: !isDisabled.value,
		onUpdate: ({ editor: ed }) => {
			bodyHtml.value = ed.getHTML()
			bumpSlot()
		},
	})
}

watch(isDisabled, (disabled) => {
	editor.value?.setEditable(!disabled)
})

watch(bodyHtml, (html) => {
	const ed = editor.value
	if (!ed) return
	if (ed.getHTML() === html) return
	ed.commands.setContent(html || DEFAULT_CARRIAGE_CONTRACT_BODY, false)
})

watch(templateEditorOpen, async (open) => {
	if (!open) return
	ensureEditor()
	await nextTick()
	editor.value?.commands.setContent(bodyHtml.value || DEFAULT_CARRIAGE_CONTRACT_BODY, false)
	editor.value?.setEditable(!isDisabled.value)
})

onBeforeUnmount(() => {
	editor.value?.destroy()
	editor.value = null
})

const openTemplateEditor = () => {
	if (templateEditorDisabledReason.value) return
	templateEditorOpen.value = true
}

const applyTemplateToBlank = () => {
	if (!editor.value) return
	bodyHtml.value = editor.value.getHTML()
	bumpSlot()
	templateEditorOpen.value = false
	useToast().add({ title: 'Текст договора обновлён', color: 'success' })
}

const resetToDefaultTemplate = () => {
	applyDefaultBody()
	editor.value?.commands.setContent(DEFAULT_CARRIAGE_CONTRACT_BODY, false)
}
</script>

<template>
	<div class="flex flex-col gap-3">
		<p class="text-sm font-semibold text-center">Договор перевозки грузов</p>

		<div v-if="childApplications.length" class="flex flex-col gap-1.5">
			<p class="text-xs text-neutral-500 text-center">Заявки к этому договору</p>
			<UButton
				v-for="app in childApplications"
				:key="app.id"
				:label="app.number ? `Открыть заявку № ${app.number}` : `Открыть заявку #${app.id}`"
				icon="i-lucide-file-plus-2"
				color="primary"
				variant="soft"
				class="w-full justify-center"
				@click="openApplication(app)"
			/>
		</div>
		<p
			v-else-if="documentId"
			class="text-xs text-neutral-500 text-center"
		>
			Заявок к договору пока нет — создайте в колонке «Договор перевозки»
		</p>

		<UTooltip
			:text="fillFromLkDisabledReason"
			:disabled="!fillFromLkDisabledReason"
		>
			<span
				class="block w-full"
				:class="{ 'cursor-not-allowed': fillFromLkDisabledReason }"
			>
				<UButton
					label="Заполнить данными"
					icon="i-lucide-database"
					color="primary"
					variant="soft"
					class="w-full justify-center pointer-events-auto"
					:disabled="Boolean(fillFromLkDisabledReason)"
					:loading="loading"
					@click="fillFromLk"
				/>
			</span>
		</UTooltip>

		<UTooltip
			:text="templateEditorDisabledReason"
			:disabled="!templateEditorDisabledReason"
		>
			<span
				class="block w-full"
				:class="{ 'cursor-not-allowed': templateEditorDisabledReason }"
			>
				<UButton
					label="Редактор текста договора"
					icon="i-lucide-file-pen-line"
					color="neutral"
					variant="subtle"
					class="w-full justify-center pointer-events-auto"
					:disabled="Boolean(templateEditorDisabledReason)"
					@click="openTemplateEditor"
				/>
			</span>
		</UTooltip>

		<UModal v-model:open="templateEditorOpen" title="ТЕКСТ ДОГОВОРА">
			<template #body>
				<div class="flex flex-col gap-3">
					<div class="flex flex-wrap gap-1">
						<UButton
							size="xs"
							variant="soft"
							color="neutral"
							label="Жирный"
							@click="editor?.chain().focus().toggleBold().run()"
						/>
						<UButton
							size="xs"
							variant="soft"
							color="neutral"
							label="Курсив"
							@click="editor?.chain().focus().toggleItalic().run()"
						/>
						<UButton
							size="xs"
							variant="soft"
							color="neutral"
							label="Список"
							@click="editor?.chain().focus().toggleBulletList().run()"
						/>
						<UButton
							size="xs"
							variant="soft"
							color="neutral"
							label="Шаблон по умолчанию"
							@click="resetToDefaultTemplate"
						/>
					</div>
					<div
						class="min-h-64 max-h-[50vh] overflow-auto rounded border border-neutral-200 p-3 prose prose-sm max-w-none"
					>
						<EditorContent v-if="editor" :editor="editor" />
					</div>
				</div>
			</template>
			<template #footer>
				<div class="flex gap-2 w-full">
					<UButton
						label="Отмена"
						color="neutral"
						variant="subtle"
						class="w-1/2"
						@click="templateEditorOpen = false"
					/>
					<UButton
						label="Применить к бланку"
						color="primary"
						class="w-1/2"
						@click="applyTemplateToBlank"
					/>
				</div>
			</template>
		</UModal>

		<UCheckbox
			:disabled="isDisabled"
			label="Реквизиты Заказчика"
			size="xl"
			v-model="customerDetailsCheck"
		/>
		<UCheckbox
			:disabled="isDisabled"
			label="Реквизиты Перевозчика"
			size="xl"
			v-model="carrierDetailsCheck"
		/>

		<p v-if="saving" class="text-xs text-neutral-500 text-center">Сохранение…</p>
	</div>
</template>
