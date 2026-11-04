<script setup lang="ts">
import { Editor as TiptapEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { TextAlign } from '@tiptap/extension-text-align'
import { useCarriageApplicationBlank } from '~/composables/useCarriageApplicationBlank'
import { DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS } from '~/utils/carriageApplicationDefaults'

/**
 * Правое меню заявки к договору (§3.2–§3.3).
 * Без «Таблица» / «СпецСим2» — только доп. условия.
 */
const {
	documentId,
	parentId,
	parentNumber,
	extraTermsHtml,
	customerDetailsCheck,
	carrierDetailsCheck,
	shipmentId,
	dealId,
	isDisabled,
	loading,
	saving,
	fillFromLk,
	refreshCargoTable,
	applyDefaultExtraTerms,
	bumpSlot,
} = useCarriageApplicationBlank()

const route = useRoute()
const router = useRouter()
const templateEditorOpen = ref(false)
const editor = shallowRef<TiptapEditor | null>(null)

const fillDisabledReason = computed(() => {
	if (!documentId.value) return 'Заявка не выбрана'
	if (loading.value) return 'Идёт загрузка…'
	return ''
})

const termsDisabledReason = computed(() => {
	if (!documentId.value) return 'Заявка не выбрана'
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
		content: extraTermsHtml.value || DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS,
		editable: !isDisabled.value,
		onUpdate: ({ editor: ed }) => {
			extraTermsHtml.value = ed.getHTML()
			bumpSlot()
		},
	})
}

watch(isDisabled, (disabled) => {
	editor.value?.setEditable(!disabled)
})

watch(extraTermsHtml, (html) => {
	const ed = editor.value
	if (!ed) return
	if (ed.getHTML() === html) return
	ed.commands.setContent(html || DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS, false)
})

watch(templateEditorOpen, async (open) => {
	if (!open) return
	ensureEditor()
	await nextTick()
	editor.value?.commands.setContent(
		extraTermsHtml.value || DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS,
		false,
	)
	editor.value?.setEditable(!isDisabled.value)
})

onBeforeUnmount(() => {
	editor.value?.destroy()
	editor.value = null
})

const openTermsEditor = () => {
	if (termsDisabledReason.value) return
	templateEditorOpen.value = true
}

const applyTerms = () => {
	if (!editor.value) return
	extraTermsHtml.value = editor.value.getHTML()
	bumpSlot()
	templateEditorOpen.value = false
	useToast().add({ title: 'Дополнительные условия обновлены', color: 'success' })
}

const resetTerms = () => {
	applyDefaultExtraTerms()
	editor.value?.commands.setContent(DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS, false)
}

const openShipments = () => {
	void router.push('/profile/shipments')
}

const openParentContract = () => {
	if (!parentId.value || !dealId.value) return
	const role = String(route.query.role || 'seller')
	void router.push({
		path: '/profile/editor',
		query: {
			dealId: String(dealId.value),
			role,
			transportDocType: 'carriage_contract',
			transportDocId: String(parentId.value),
		},
		hash: '#contract',
	})
}
</script>

<template>
	<div class="flex flex-col gap-3">
		<p class="text-sm font-semibold text-center">Заявка к договору перевозки</p>

		<UButton
			v-if="parentId"
			:label="parentNumber ? `Открыть договор № ${parentNumber}` : 'Открыть рамочный договор'"
			icon="i-lucide-file-text"
			color="neutral"
			variant="soft"
			class="w-full justify-center"
			@click="openParentContract"
		/>

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

		<UButton
			label="Обновить таблицу перевозки"
			icon="i-lucide-refresh-cw"
			color="neutral"
			variant="subtle"
			class="w-full justify-center"
			:disabled="!documentId || loading"
			@click="refreshCargoTable"
		/>

		<UButton
			label="Редактировать данные перевозки"
			icon="i-lucide-truck"
			color="neutral"
			variant="subtle"
			class="w-full justify-center"
			:disabled="!documentId"
			@click="openShipments"
		/>
		<p v-if="shipmentId" class="text-xs text-neutral-500 text-center">
			К заказу привязана перевозка — таблица заполняется из неё
		</p>
		<p v-else class="text-xs text-amber-700 text-center">
			К этому заказу ещё не привязана перевозка — таблица пустая.
			Создайте или привяжите её в разделе
			<button
				type="button"
				class="underline underline-offset-2 hover:text-amber-900 font-medium"
				@click="openShipments"
			>
				«Перевозки»
			</button>.
		</p>

		<UTooltip :text="termsDisabledReason" :disabled="!termsDisabledReason">
			<span class="block w-full" :class="{ 'cursor-not-allowed': termsDisabledReason }">
				<UButton
					label="Редактор доп. условий"
					icon="i-lucide-file-pen-line"
					color="neutral"
					variant="subtle"
					class="w-full justify-center"
					:disabled="Boolean(termsDisabledReason)"
					@click="openTermsEditor"
				/>
			</span>
		</UTooltip>

		<UModal v-model:open="templateEditorOpen" title="ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ">
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
							@click="resetTerms"
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
						@click="applyTerms"
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
