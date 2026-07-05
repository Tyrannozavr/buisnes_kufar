<template>
	<div class="flex flex-col gap-3 text-center">
		<p>Фото/Сканы документа</p>

		<p v-if="loading" class="text-xs text-neutral-500" role="status">Загрузка…</p>

		<ul v-if="savedScans.length" class="flex flex-col gap-2 text-left">
			<li
				v-for="scan in savedScans"
				:key="scan.document_id"
				class="flex flex-col gap-1 rounded border border-neutral-200 dark:border-neutral-700 p-2 text-sm"
			>
				<span class="truncate font-medium" :title="scanLabel(scan)">
					{{ scanLabel(scan) }}
				</span>
				<div class="flex flex-wrap gap-1">
					<UButton
						label="Просмотр"
						icon="i-lucide-eye"
						size="xs"
						color="neutral"
						variant="soft"
						@click="openViewer(scan)"
					/>
					<UButton
						label="Сохранить локально"
						icon="i-lucide-download"
						size="xs"
						color="neutral"
						variant="soft"
						@click="downloadScan(scan)"
					/>
					<UButton
						v-if="canModify"
						label="Удалить"
						icon="i-lucide-trash-2"
						size="xs"
						color="error"
						variant="soft"
						:loading="deletingId === scan.document_id"
						@click="removeScan(scan)"
					/>
					<UButton
						v-if="canModify"
						label="Отправить контрагенту"
						icon="i-lucide-send"
						size="xs"
						color="primary"
						variant="soft"
						:loading="sendingId === scan.document_id"
						@click="notifyCounterpart(scan)"
					/>
				</div>
			</li>
		</ul>

		<template v-if="canModify">
			<input
				ref="fileInputRef"
				type="file"
				class="hidden"
				accept="image/*,.pdf,application/pdf"
				aria-label="Выберите файл скана"
				@change="onFilePicked"
			/>
			<UTooltip
				text="Перейдите в режим редактирования"
				:disabled="editEnabled || uploading"
			>
				<span
					class="block w-full"
					:class="{ 'cursor-not-allowed': !editEnabled || uploading }"
				>
					<UButton
						label="Выберите файл"
						icon="i-lucide-folder-search"
						color="neutral"
						variant="subtle"
						size="xl"
						class="justify-center w-full pointer-events-auto"
						:disabled="!editEnabled || uploading"
						@click="fileInputRef?.click()"
					/>
				</span>
			</UTooltip>

			<div
				v-if="pendingPreviewUrl"
				class="rounded border border-dashed border-neutral-300 p-2 text-left text-sm space-y-2"
			>
				<p class="truncate font-medium">{{ pendingFile?.name }}</p>
				<img
					v-if="pendingIsImage"
					:src="pendingPreviewUrl"
					:alt="pendingFile?.name"
					class="max-h-32 mx-auto object-contain"
				/>
				<p v-else class="text-xs text-neutral-500">PDF — предпросмотр после сохранения</p>
				<div class="flex flex-wrap gap-1 justify-center">
					<UButton
						label="Сохранить локально"
						icon="i-lucide-save"
						size="sm"
						color="primary"
						variant="soft"
						:loading="uploading"
						@click="savePendingLocally"
					/>
					<UButton
						label="Отправить контрагенту"
						icon="i-lucide-send"
						size="sm"
						color="success"
						variant="soft"
						:loading="uploading"
						@click="savePendingAndNotify"
					/>
					<UButton
						label="Отмена"
						icon="i-lucide-x"
						size="sm"
						color="neutral"
						variant="ghost"
						:disabled="uploading"
						@click="clearPending"
					/>
				</div>
			</div>
		</template>

		<p v-else-if="!savedScans.length && !loading" class="text-xs text-neutral-500">
			Сканы пока не загружены
		</p>

		<FileViewer
			v-if="viewerOpen"
			:is-modal-open="viewerOpen"
			:deal-id="viewerDealId"
			:document-id="viewerDocumentId"
			:name="viewerName"
			:type="viewerType"
			@update:is-modal-open="viewerOpen = $event"
			@close="viewerOpen = false"
		/>
	</div>
</template>

<script setup lang="ts">
import { useQuery, useQueryCache } from "@pinia/colada"
import { useRoute } from "vue-router"
import FileViewer from "~/components/ui/File-viewer.vue"
import { useDocumentsApi } from "~/api/documents"
import { uploadDocumentByIdQuery, deleteDocumentQuery } from "~/queries/documents"
import { QueryKeys } from "~/constants/queryKeys"
import type { DocumentApiItem, DocumentTypeResponse } from "~/types/documents"
import {
	getCounterpartData,
	sendScanToCounterpart,
} from "~/utils/counterpart"

const props = defineProps<{
	dealId: number
	documentType: Extract<DocumentTypeResponse, "order" | "bill">
	readOnly: boolean
	editEnabled: boolean
}>()

const route = useRoute()
const toast = useToast()
const queryCache = useQueryCache()
const documentsApi = useDocumentsApi()
const { uploadDocumentById } = uploadDocumentByIdQuery()
const { deleteDocumentAsync } = deleteDocumentQuery()

const fileInputRef = ref<HTMLInputElement | null>(null)
const pendingFile = ref<File | null>(null)
const pendingPreviewUrl = ref<string | null>(null)
const uploading = ref(false)
const deletingId = ref<number | null>(null)
const sendingId = ref<number | null>(null)

const viewerOpen = ref(false)
const viewerDealId = ref(0)
const viewerDocumentId = ref(0)
const viewerName = ref("")
const viewerType = ref("")

const canModify = computed(() => !props.readOnly)

const { data: documents, asyncStatus, refetch } = useQuery({
	key: () => [QueryKeys.GET_DOCUMENTS_BY_DEAL_ID, props.dealId],
	query: () => useDocumentsApi().getDocumentsByDealId(props.dealId),
	enabled: () => props.dealId > 0,
})

const loading = computed(() => asyncStatus.value === "loading")

const savedScans = computed(() =>
	(documents.value ?? []).filter(
		(doc) =>
			doc.document_type === props.documentType &&
			Boolean(doc.document_file_path?.trim()),
	),
)

const pendingIsImage = computed(() => {
	const type = pendingFile.value?.type ?? ""
	return type.startsWith("image/")
})

const scanLabel = (scan: DocumentApiItem): string => {
	const path = scan.document_file_path ?? ""
	const name = path.split("/").pop() ?? `Скан #${scan.document_id}`
	return scan.document_number?.trim() ? `${scan.document_number} (${name})` : name
}

const fileExtension = (path: string | null): string => {
	if (!path) return ""
	const ext = path.split(".").pop()?.toLowerCase() ?? ""
	return ext === "jpg" ? "jpeg" : ext
}

const refreshDocuments = async (): Promise<void> => {
	queryCache.invalidateQueries({
		key: [QueryKeys.GET_DOCUMENTS_BY_DEAL_ID, props.dealId],
	})
	await refetch()
}

const clearPending = (): void => {
	if (pendingPreviewUrl.value) {
		URL.revokeObjectURL(pendingPreviewUrl.value)
	}
	pendingFile.value = null
	pendingPreviewUrl.value = null
	if (fileInputRef.value) {
		fileInputRef.value.value = ""
	}
}

const onFilePicked = (event: Event): void => {
	const input = event.target as HTMLInputElement
	const file = input.files?.[0]
	if (!file) return
	clearPending()
	pendingFile.value = file
	if (file.type.startsWith("image/")) {
		pendingPreviewUrl.value = URL.createObjectURL(file)
	} else {
		pendingPreviewUrl.value = "pdf"
	}
}

const uploadPending = async (): Promise<number | null> => {
	if (!pendingFile.value || !props.dealId) return null
	const formData = new FormData()
	formData.append("file", pendingFile.value)
	formData.append("document_type", props.documentType)
	uploading.value = true
	try {
		const response = await uploadDocumentById(props.dealId, formData)
		const id = response?.document_id ?? null
		if (!id) return null
		await refreshDocuments()
		clearPending()
		return id
	} catch (error) {
		toast.add({
			title: "Не удалось сохранить скан",
			description: "Проверьте, что S3/MinIO настроен в dev",
			color: "error",
		})
		if (import.meta.dev) console.error("upload scan:", error)
		return null
	} finally {
		uploading.value = false
	}
}

const savePendingLocally = async (): Promise<void> => {
	const id = await uploadPending()
	if (id) {
		toast.add({ title: "Скан сохранён", color: "success" })
	}
}

const savePendingAndNotify = async (): Promise<void> => {
	if (!pendingFile.value) return
	const filename = pendingFile.value.name
	const id = await uploadPending()
	if (!id) return

	const dealId = props.dealId
	const role = route.query.role as "buyer" | "seller"
	const counterpart = getCounterpartData(dealId, role)
	if (!counterpart?.companyId) {
		toast.add({ title: "Скан сохранён", color: "success" })
		return
	}
	try {
		await sendScanToCounterpart(
			dealId,
			role,
			counterpart,
			props.documentType,
			filename,
		)
		toast.add({ title: "Скан сохранён и отправлен контрагенту", color: "success" })
	} catch (error) {
		toast.add({
			title: "Скан сохранён, но сообщение в чат не отправлено",
			color: "warning",
		})
		if (import.meta.dev) console.error("notify scan after upload:", error)
	}
}

const openViewer = (scan: DocumentApiItem): void => {
	viewerDealId.value = scan.deal_id
	viewerDocumentId.value = scan.document_id
	viewerName.value = scanLabel(scan)
	viewerType.value = fileExtension(scan.document_file_path)
	viewerOpen.value = true
}

const downloadScan = async (scan: DocumentApiItem): Promise<void> => {
	try {
		const result = await documentsApi.downloadDocument(
			scan.deal_id,
			scan.document_id,
			true,
		)
		if (!(result instanceof Blob)) {
			throw new Error("Не удалось получить файл")
		}
		const url = URL.createObjectURL(result)
		const anchor = document.createElement("a")
		anchor.href = url
		anchor.download = scanLabel(scan)
		anchor.click()
		URL.revokeObjectURL(url)
	} catch (error) {
		toast.add({ title: "Не удалось скачать файл", color: "error" })
		if (import.meta.dev) console.error("download scan:", error)
	}
}

const removeScan = async (scan: DocumentApiItem): Promise<void> => {
	deletingId.value = scan.document_id
	try {
		await deleteDocumentAsync(scan.deal_id, scan.document_id)
		await refreshDocuments()
		toast.add({ title: "Скан удалён", color: "success" })
	} catch (error) {
		toast.add({ title: "Не удалось удалить скан", color: "error" })
		if (import.meta.dev) console.error("delete scan:", error)
	} finally {
		deletingId.value = null
	}
}

const notifyCounterpart = async (scan: DocumentApiItem): Promise<void> => {
	const dealId = props.dealId
	const role = route.query.role as "buyer" | "seller"
	const counterpart = getCounterpartData(dealId, role)
	if (!counterpart?.companyId) {
		toast.add({
			title: "Контрагент не найден",
			color: "warning",
		})
		return
	}
	sendingId.value = scan.document_id
	try {
		await sendScanToCounterpart(
			dealId,
			role,
			counterpart,
			props.documentType,
			scanLabel(scan),
		)
		toast.add({ title: "Скан отправлен контрагенту в чат", color: "success" })
	} catch (error) {
		toast.add({ title: "Не удалось отправить сообщение в чат", color: "error" })
		if (import.meta.dev) console.error("notify scan:", error)
	} finally {
		sendingId.value = null
	}
}

onUnmounted(() => {
	clearPending()
})
</script>
