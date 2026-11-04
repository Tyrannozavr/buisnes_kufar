<script setup lang="ts">
import { Editor as TiptapEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { TextAlign } from '@tiptap/extension-text-align'
import { useExpeditionContractBlank } from '~/composables/useExpeditionContractBlank'
import { DEFAULT_EXPEDITION_CONTRACT_BODY } from '~/utils/expeditionContractDefaults'

/** Правое меню договора экспедиции (§4.2 / §4.3). */
const {
	documentId,
	bodyHtml,
	clientDetailsCheck,
	forwarderDetailsCheck,
	isDisabled,
	loading,
	saving,
	fillFromLk,
	applyDefaultBody,
	bumpSlot,
} = useExpeditionContractBlank()

const templateEditorOpen = ref(false)
const editor = shallowRef<TiptapEditor | null>(null)

const fillDisabledReason = computed(() => {
	if (!documentId.value) return 'Договор экспедиции не выбран'
	if (loading.value) return 'Идёт загрузка…'
	return ''
})

const templateEditorDisabledReason = computed(() => {
	if (!documentId.value) return 'Договор экспедиции не выбран'
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
		content: bodyHtml.value || DEFAULT_EXPEDITION_CONTRACT_BODY,
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
	ed.commands.setContent(html || DEFAULT_EXPEDITION_CONTRACT_BODY, false)
})

watch(templateEditorOpen, async (open) => {
	if (!open) return
	ensureEditor()
	await nextTick()
	editor.value?.commands.setContent(
		bodyHtml.value || DEFAULT_EXPEDITION_CONTRACT_BODY,
		false,
	)
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

const applyBody = () => {
	if (!editor.value) return
	bodyHtml.value = editor.value.getHTML()
	bumpSlot()
	templateEditorOpen.value = false
	useToast().add({ title: 'Текст договора обновлён', color: 'success' })
}

const resetBody = () => {
	applyDefaultBody()
	editor.value?.commands.setContent(DEFAULT_EXPEDITION_CONTRACT_BODY, false)
}
</script>

<template>
	<div class="flex flex-col gap-3">
		<p class="text-sm font-semibold text-center">Договор транспортной экспедиции</p>

		<UTooltip :text="fillDisabledReason" :disabled="!fillDisabledReason">
			<span class="block w-full" :class="{ 'cursor-not-allowed': fillDisabledReason }">
				<UButton
					label="Заполнить данными"
					icon="i-lucide-database"
					color="primary"
					variant="soft"
					class="w-full justify-center"
					:disabled="Boolean(fillDisabledReason)"
					:loading="loading"
					@click="fillFromLk"
				/>
			</span>
		</UTooltip>

		<UTooltip :text="templateEditorDisabledReason" :disabled="!templateEditorDisabledReason">
			<span class="block w-full" :class="{ 'cursor-not-allowed': templateEditorDisabledReason }">
				<UButton
					label="Редактор текста договора"
					icon="i-lucide-file-pen-line"
					color="neutral"
					variant="subtle"
					class="w-full justify-center"
					:disabled="Boolean(templateEditorDisabledReason)"
					@click="openTemplateEditor"
				/>
			</span>
		</UTooltip>

		<UModal v-model:open="templateEditorOpen" title="ТЕКСТ ДОГОВОРА">
			<template #body>
				<div class="flex flex-col gap-3">
					<div class="flex flex-wrap gap-1">
						<UButton size="xs" variant="soft" color="neutral" label="Жирный" @click="editor?.chain().focus().toggleBold().run()" />
						<UButton size="xs" variant="soft" color="neutral" label="Курсив" @click="editor?.chain().focus().toggleItalic().run()" />
						<UButton size="xs" variant="soft" color="neutral" label="Список" @click="editor?.chain().focus().toggleBulletList().run()" />
						<UButton size="xs" variant="soft" color="neutral" label="Шаблон по умолчанию" @click="resetBody" />
					</div>
					<div class="min-h-64 max-h-[50vh] overflow-auto rounded border border-neutral-200 p-3 prose prose-sm max-w-none">
						<EditorContent v-if="editor" :editor="editor" />
					</div>
				</div>
			</template>
			<template #footer>
				<div class="flex gap-2 w-full">
					<UButton label="Отмена" color="neutral" variant="subtle" class="w-1/2" @click="templateEditorOpen = false" />
					<UButton label="Применить к бланку" color="primary" class="w-1/2" @click="applyBody" />
				</div>
			</template>
		</UModal>

		<UCheckbox :disabled="isDisabled" label="Реквизиты Клиента" size="xl" v-model="clientDetailsCheck" />
		<UCheckbox :disabled="isDisabled" label="Реквизиты Экспедитора" size="xl" v-model="forwarderDetailsCheck" />

		<p v-if="saving" class="text-xs text-neutral-500 text-center">Сохранение…</p>
	</div>
</template>
