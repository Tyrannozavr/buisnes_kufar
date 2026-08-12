/** Публичный URL загруженного файла (чат и др.). */
export function publicFileUrl(url?: string | null): string {
	if (!url) return ''
	const value = url.trim()
	if (!value) return ''
	if (value.startsWith('/')) return value
	try {
		const parsed = new URL(value)
		if (parsed.pathname.startsWith('/uploads/')) {
			return parsed.pathname
		}
	} catch {
		// relative or malformed — fall through
	}
	if (value.startsWith('uploads/')) return `/${value}`
	return value
}
