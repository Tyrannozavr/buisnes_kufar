<script setup lang="ts">
import { useDocumentsApi } from "~/api/documents"

const props = defineProps<{
	isModalOpen: boolean
	name?: string
	type?: string
	dealId: number
	documentId: number
}>()

const emit = defineEmits<{
	(e: "close"): void
	(e: "update:isModalOpen", value: boolean): void
}>()

const { downloadDocument } = useDocumentsApi()
const blobUrl = ref<string | null>(null)
const loading = ref(false)
const loadError = ref(false)

const isImageType = computed(() => {
	const t = (props.type ?? "").toLowerCase()
	return ["jpeg", "jpg", "png", "gif", "webp", "bmp"].includes(t)
})

const isPdfType = computed(() => (props.type ?? "").toLowerCase() === "pdf")

const modalOpen = computed({
	get: () => props.isModalOpen,
	set: (value: boolean) => {
		if (!value) handleClose()
	},
})

const revokeBlobUrl = (): void => {
	if (blobUrl.value) {
		URL.revokeObjectURL(blobUrl.value)
		blobUrl.value = null
	}
}

const loadPreview = async (): Promise<void> => {
	if (!props.isModalOpen || !props.dealId || !props.documentId) return

	loading.value = true
	loadError.value = false
	revokeBlobUrl()

	try {
		const result = await downloadDocument(props.dealId, props.documentId, true)
		const blob =
			result instanceof Blob
				? result
				: result != null
					? new Blob([result as BlobPart])
					: null
		if (!blob || blob.size === 0) {
			throw new Error("Не удалось получить файл")
		}
		blobUrl.value = URL.createObjectURL(blob)
	} catch (error) {
		loadError.value = true
		if (import.meta.dev) console.error("File-viewer load:", error)
	} finally {
		loading.value = false
	}
}

watch(
	() => [props.isModalOpen, props.dealId, props.documentId] as const,
	([open]) => {
		if (open) {
			void loadPreview()
		} else {
			revokeBlobUrl()
			loadError.value = false
			loading.value = false
		}
	},
	{ immediate: true },
)

const handleClose = (): void => {
	emit("update:isModalOpen", false)
	emit("close")
}

onUnmounted(() => {
	revokeBlobUrl()
})
</script>

<template>
	<UModal
		v-model:open="modalOpen"
		fullscreen
		size="4xl"
	>
		<template #header>
			<div class="flex items-center justify-between w-full">
				<h3 class="text-xl font-semibold">Просмотр документа: {{ name }}</h3>
				<UButton
					color="neutral"
					variant="ghost"
					icon="i-heroicons-x-mark"
					@click="handleClose"
				/>
			</div>
		</template>

		<template #body>
			<p v-if="loading" class="text-center text-neutral-500 py-8">Загрузка…</p>
			<p v-else-if="loadError" class="text-center text-red-500 py-8">
				Не удалось открыть файл. Попробуйте «Сохранить локально».
			</p>
			<div
				v-else-if="blobUrl && isPdfType"
				class="h-[80vh] min-h-0 overflow-hidden flex flex-col"
			>
				<iframe :src="blobUrl" class="w-full flex-1 min-h-0 border-0" />
			</div>
			<div v-else-if="blobUrl && isImageType" class="flex justify-center p-4">
				<img :src="blobUrl" :alt="name" class="max-h-[80vh] object-contain" />
			</div>
			<p v-else-if="blobUrl" class="text-center text-neutral-500 py-8">
				Предпросмотр недоступен для этого типа файла. Используйте «Сохранить локально».
			</p>
		</template>
	</UModal>
</template>
