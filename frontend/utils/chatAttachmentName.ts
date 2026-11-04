import { extractChatScanRefs } from './chatScanMarker'

/** UUID storage-имя вроде a3dca4ca3dc942d8b2cd616e2b9dd63f.png */
export function isStorageFileName(name?: string | null): boolean {
	if (!name) return false
	return /^[a-f0-9]{32}\.[a-z0-9]+$/i.test(name.trim())
}

/** Имя для UI/скачивания: маркер скана или file_name, не internal UUID. */
export function chatAttachmentDisplayName(message: {
	content?: string | null
	file_name?: string | null
}): string {
	const fromMarker = extractChatScanRefs(message.content || '')[0]?.filename?.trim()
	const stored = (message.file_name || '').trim()

	if (stored && !isStorageFileName(stored)) return stored
	if (fromMarker && !isStorageFileName(fromMarker)) return fromMarker
	// Старые сообщения, где везде остался UUID storage — не показываем его
	if (stored || fromMarker) return 'Скан'
	return 'Файл'
}
