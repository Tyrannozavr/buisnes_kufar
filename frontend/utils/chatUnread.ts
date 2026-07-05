import type { RouteLocationNormalizedLoaded } from 'vue-router'

export function getActiveChatIdFromRoute(
	route: RouteLocationNormalizedLoaded,
): number | null {
	const match = route.path.match(/^\/profile\/messages\/(\d+)\/?$/)
	if (!match) return null
	const id = Number(match[1])
	return Number.isFinite(id) ? id : null
}

export function isChatPageVisible(chatId: number | null): boolean {
	if (!import.meta.client || chatId == null) return false
	if (document.visibilityState !== 'visible') return false
	return getActiveChatIdFromRoute(useRoute()) === chatId
}
