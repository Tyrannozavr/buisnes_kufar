<script setup lang="ts">
import { publicFileUrl } from '~/utils/publicFileUrl'

const props = defineProps<{
	filePath?: string | null
	fileName?: string | null
	/** Человекочитаемое имя (исходный файл); если нет — fileName. */
	displayName?: string | null
	fileSize?: number | null
	fileType?: string | null
	/** Копия ещё пишется в chat_files (есть маркер скана, file_path пока нет). */
	pendingCopy?: boolean
	isMine?: boolean
}>()

const label = computed(
	() => (props.displayName || props.fileName || 'Файл').trim() || 'Файл',
)

const emit = defineEmits<{
	loaded: []
	failed: []
}>()

const status = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const downloading = ref(false)
const imgRef = ref<HTMLImageElement | null>(null)
const resolvedSrc = computed(() => publicFileUrl(props.filePath))

const isImage = computed(() => {
	const type = (props.fileType || '').toLowerCase()
	const name = (props.fileName || props.filePath || props.displayName || '').toLowerCase()
	return type.startsWith('image/') || /\.(jpe?g|png|gif|webp|bmp|svg)$/i.test(name)
})

const mutedClass = computed(() =>
	props.isMine ? 'text-blue-100' : 'text-gray-500',
)

const markReady = () => {
	if (status.value === 'ready') return
	status.value = 'ready'
	emit('loaded')
}

const markError = () => {
	status.value = 'error'
	emit('failed')
}

/** Если браузер уже закэшировал картинку — @load мог не прийти. */
const syncFromImgEl = () => {
	const el = imgRef.value
	if (!el || !resolvedSrc.value) return
	if (el.complete && el.naturalWidth > 0) {
		markReady()
		return
	}
	if (el.complete && el.naturalWidth === 0) {
		markError()
	}
}

watch(
	() => [props.filePath, props.pendingCopy, isImage.value] as const,
	([path, pending, image]) => {
		if (pending && !path) {
			status.value = 'loading'
			return
		}
		if (path && image) {
			status.value = 'loading'
			nextTick(() => syncFromImgEl())
			return
		}
		if (path) {
			status.value = 'ready'
			return
		}
		status.value = 'idle'
	},
	{ immediate: true },
)

const formatFileSize = (bytes: number) => {
	if (!bytes) return ''
	const units = ['B', 'KB', 'MB', 'GB']
	let size = bytes
	let i = 0
	while (size >= 1024 && i < units.length - 1) {
		size /= 1024
		i += 1
	}
	return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

/** Надёжное скачивание с нужным именем (StaticFiles отдаёт inline). */
const downloadFile = async () => {
	if (!resolvedSrc.value || downloading.value) return
	downloading.value = true
	try {
		const response = await fetch(resolvedSrc.value)
		if (!response.ok) throw new Error(`HTTP ${response.status}`)
		const blob = await response.blob()
		const url = URL.createObjectURL(blob)
		const anchor = document.createElement('a')
		anchor.href = url
		anchor.download = label.value
		anchor.rel = 'noopener'
		document.body.appendChild(anchor)
		anchor.click()
		anchor.remove()
		URL.revokeObjectURL(url)
	} catch (error) {
		// fallback: открыть в новой вкладке
		window.open(resolvedSrc.value, '_blank', 'noopener,noreferrer')
		if (import.meta.dev) console.error('chat attachment download:', error)
	} finally {
		downloading.value = false
	}
}
</script>

<template>
	<div class="mt-1 max-w-[16rem]">
		<div
			v-if="pendingCopy && !filePath"
			class="flex h-28 items-center justify-center gap-2 rounded-lg bg-black/10 px-3"
			role="status"
		>
			<UIcon name="i-heroicons-arrow-path" class="h-5 w-5 animate-spin opacity-80" />
			<span class="text-xs" :class="mutedClass">Готовим вложение…</span>
		</div>

		<template v-else-if="filePath && isImage">
			<a
				:href="status === 'ready' ? resolvedSrc : undefined"
				:target="status === 'ready' ? '_blank' : undefined"
				rel="noopener noreferrer"
				class="relative block overflow-hidden rounded-lg min-h-28"
				:class="status !== 'ready' ? 'pointer-events-none' : ''"
				:title="status === 'ready' ? 'Открыть' : undefined"
			>
				<div
					v-if="status !== 'ready'"
					class="absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-neutral-300/90"
					aria-hidden="true"
				>
					<UIcon
						v-if="status === 'loading'"
						name="i-heroicons-arrow-path"
						class="h-6 w-6 animate-spin text-neutral-500"
					/>
					<UIcon
						v-else
						name="i-heroicons-photo"
						class="h-8 w-8 text-neutral-500"
					/>
				</div>
				<img
					ref="imgRef"
					:src="resolvedSrc"
					:alt="label"
					class="relative z-0 max-h-52 w-auto max-w-full object-contain rounded-lg bg-black/10"
					:class="status === 'ready' ? 'opacity-100' : 'opacity-0'"
					@load="markReady"
					@error="markError"
				/>
			</a>
			<div class="mt-1.5 flex items-center gap-2 min-w-0">
				<p class="min-w-0 flex-1 text-xs truncate opacity-80" :class="mutedClass">
					{{ label }}
					<span v-if="fileSize"> · {{ formatFileSize(fileSize) }}</span>
				</p>
				<button
					type="button"
					class="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors"
					:class="isMine
						? 'bg-white/15 text-blue-50 hover:bg-white/25'
						: 'bg-white text-blue-700 hover:bg-blue-50 border border-blue-200'"
					:disabled="status === 'loading' || downloading"
					:title="`Скачать ${label}`"
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
			<p
				v-if="status === 'error'"
				class="mt-0.5 text-xs opacity-80"
				:class="isMine ? 'text-blue-100' : 'text-amber-700'"
			>
				Превью недоступно
			</p>
		</template>

		<div
			v-else-if="filePath"
			class="flex items-center gap-2 p-2 rounded max-w-full"
			:class="isMine ? 'bg-white/10 text-blue-100' : 'bg-white text-gray-800 border border-gray-200'"
		>
			<UIcon name="i-heroicons-document" class="w-5 h-5 shrink-0 opacity-80" />
			<div class="flex-1 min-w-0">
				<p class="text-sm font-medium truncate">{{ label }}</p>
				<p v-if="fileSize" class="text-xs opacity-75">{{ formatFileSize(fileSize) }}</p>
			</div>
			<button
				type="button"
				class="inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
				:class="isMine
					? 'bg-white/15 text-blue-50 hover:bg-white/25'
					: 'bg-blue-50 text-blue-700 hover:bg-blue-100'"
				:disabled="downloading"
				:title="`Скачать ${label}`"
				@click="downloadFile"
			>
				<UIcon
					:name="downloading ? 'i-heroicons-arrow-path' : 'i-heroicons-arrow-down-tray'"
					class="h-4 w-4"
					:class="downloading ? 'animate-spin' : ''"
				/>
				Скачать
			</button>
		</div>
	</div>
</template>
