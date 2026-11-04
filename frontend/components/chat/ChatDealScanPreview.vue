<script setup lang="ts">
import { useDocumentsApi } from '~/api/documents'

const props = defineProps<{
	dealId: number
	documentId: number
	filename: string
	isMine?: boolean
}>()

const documentsApi = useDocumentsApi()
const objectUrl = ref<string | null>(null)
const blobRef = ref<Blob | null>(null)
const loading = ref(true)
const failed = ref(false)
const downloading = ref(false)
const isImage = ref(false)

const load = async () => {
	loading.value = true
	failed.value = false
	blobRef.value = null
	if (objectUrl.value) {
		URL.revokeObjectURL(objectUrl.value)
		objectUrl.value = null
	}
	try {
		const blob = await documentsApi.downloadDocument(
			props.dealId,
			props.documentId,
			true,
		)
		if (!(blob instanceof Blob)) {
			failed.value = true
			return
		}
		blobRef.value = blob
		isImage.value = blob.type.startsWith('image/')
		objectUrl.value = URL.createObjectURL(blob)
	} catch {
		failed.value = true
	} finally {
		loading.value = false
	}
}

const downloadFile = () => {
	if (!blobRef.value || downloading.value) return
	downloading.value = true
	try {
		const url = URL.createObjectURL(blobRef.value)
		const anchor = document.createElement('a')
		anchor.href = url
		anchor.download = props.filename || 'scan'
		document.body.appendChild(anchor)
		anchor.click()
		anchor.remove()
		URL.revokeObjectURL(url)
	} finally {
		downloading.value = false
	}
}

watch(
	() => [props.dealId, props.documentId],
	() => {
		void load()
	},
	{ immediate: true },
)

onBeforeUnmount(() => {
	if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
})
</script>

<template>
	<div class="mt-2 max-w-[16rem]">
		<p
			v-if="loading"
			class="text-xs opacity-80"
			:class="isMine ? 'text-blue-100' : 'text-gray-500'"
		>
			Загрузка превью…
		</p>
		<p
			v-else-if="failed"
			class="text-xs opacity-80"
			:class="isMine ? 'text-blue-100' : 'text-amber-700'"
		>
			Превью недоступно — откройте по ссылке «Открыть сканы»
		</p>
		<template v-else-if="objectUrl">
			<a
				v-if="isImage"
				:href="objectUrl"
				target="_blank"
				rel="noopener noreferrer"
				class="block overflow-hidden rounded-lg"
				title="Открыть"
			>
				<img
					:src="objectUrl"
					:alt="filename"
					class="max-h-52 w-auto max-w-full object-contain rounded-lg bg-black/10"
					loading="lazy"
				/>
			</a>
			<div
				v-else
				class="flex items-center gap-2 p-2 rounded"
				:class="isMine ? 'bg-white/10 text-blue-100' : 'bg-white/60 text-blue-700'"
			>
				<UIcon name="i-heroicons-document" class="w-5 h-5 shrink-0" />
				<span class="text-sm truncate flex-1 min-w-0">{{ filename }}</span>
			</div>
			<div class="mt-1.5 flex items-center gap-2 min-w-0">
				<p
					class="min-w-0 flex-1 text-xs truncate opacity-80"
					:class="isMine ? 'text-blue-100' : 'text-gray-500'"
				>
					{{ filename }}
				</p>
				<button
					type="button"
					class="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors"
					:class="isMine
						? 'bg-white/15 text-blue-50 hover:bg-white/25'
						: 'bg-white text-blue-700 hover:bg-blue-50 border border-blue-200'"
					:disabled="downloading"
					:title="`Скачать ${filename}`"
					@click.stop="downloadFile"
				>
					<UIcon
						:name="downloading ? 'i-heroicons-arrow-path' : 'i-heroicons-arrow-down-tray'"
						class="h-3.5 w-3.5"
						:class="downloading ? 'animate-spin' : ''"
					/>
					Скачать
				</button>
			</div>
		</template>
	</div>
</template>
