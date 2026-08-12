/** Превью последней строки в списке чатов. */
export function chatLastMessagePreview(message?: {
	content?: string | null
	file_name?: string | null
	file_type?: string | null
} | null): string {
	const content = (message?.content || '').trim()
	if (content) return content

	const type = (message?.file_type || '').toLowerCase()
	const name = (message?.file_name || '').toLowerCase()
	if (type.startsWith('image/') || /\.(jpe?g|png|gif|webp|bmp|svg)$/i.test(name)) {
		return 'Изображение'
	}
	if (message?.file_name || message?.file_type) {
		return 'Файл'
	}
	return 'Нет сообщений'
}
