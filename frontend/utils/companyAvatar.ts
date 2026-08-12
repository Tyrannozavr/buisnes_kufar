/** Единый fallback аватара компании в чатах (пустой/битый URL → заглушка). */
export const DEFAULT_COMPANY_LOGO = '/images/default-company-logo.png'

export function companyAvatarUrl(url?: string | null): string {
	const value = (url || '').trim()
	return value || DEFAULT_COMPANY_LOGO
}

export function onCompanyAvatarError(event: Event) {
	const img = event.target as HTMLImageElement | null
	if (!img || img.dataset.avatarFallback === '1') return
	// Один раз: битый logo_url → публичная заглушка (без IPX / NuxtImg)
	img.dataset.avatarFallback = '1'
	img.src = DEFAULT_COMPANY_LOGO
}
