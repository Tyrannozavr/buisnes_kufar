export type EditorTabId = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
export type EditorDocumentTab = 'order' | 'bill' | 'supply_contract'

export const EDITOR_PATH = '/profile/editor'

export const HASH_TO_TAB: Record<string, EditorTabId> = {
	'#order': '0',
	'#bill': '1',
	'#supplyContract': '2',
	'#accompanyingDocuments': '3',
	'#invoice': '4',
	'#contract': '5',
	'#act': '6',
	'#othersDocument': '7',
}

export const TAB_TO_HASH: Record<EditorTabId, string> = {
	'0': '#order',
	'1': '#bill',
	'2': '#supplyContract',
	'3': '#accompanyingDocuments',
	'4': '#invoice',
	'5': '#contract',
	'6': '#act',
	'7': '#othersDocument',
}

export const DOCUMENT_TAB_TO_EDITOR_TAB: Record<EditorDocumentTab, EditorTabId> = {
	order: '0',
	bill: '1',
	supply_contract: '2',
}

export const tabFromQuery = (
	tabQuery?: string | string[] | null,
): EditorTabId | null => {
	const queryTab = Array.isArray(tabQuery) ? tabQuery[0] : tabQuery
	if (queryTab === 'order') return '0'
	if (queryTab === 'bill') return '1'
	return null
}

/**
 * Вкладка из URL. Если hash и ?tab= временно расходятся (router.replace
 * обновляет их не атомарно) — возвращаем null, чтобы не откатить activeTab.
 */
export const tabFromRoute = (
	hash: string,
	tabQuery?: string | string[] | null,
): EditorTabId | null => {
	const fromHash = HASH_TO_TAB[hash] ?? null
	const fromQuery = tabFromQuery(tabQuery)
	if (fromHash && fromQuery && fromHash !== fromQuery) {
		return null
	}
	return fromHash ?? fromQuery
}

export const buildEditorDealUrl = (
	dealId: number,
	role: 'buyer' | 'seller',
	documentTab: EditorDocumentTab,
): string => {
	const params = new URLSearchParams({
		dealId: String(dealId),
		role,
		tab: documentTab,
	})
	const hash =
		documentTab === 'order'
			? '#order'
			: documentTab === 'bill'
				? '#bill'
				: '#supplyContract'
	return `${EDITOR_PATH}?${params.toString()}${hash}`
}

export const buildEditorDealAbsoluteUrl = (
	dealId: number,
	role: 'buyer' | 'seller',
	documentTab: EditorDocumentTab,
): string => {
	const relative = buildEditorDealUrl(dealId, role, documentTab)
	if (import.meta.client && typeof window !== 'undefined') {
		return new URL(relative, window.location.origin).toString()
	}
	return relative
}

/** Внутренняя ссылка на редактор (для чата) — без target=_blank. */
export const isInternalAppUrl = (url: string): boolean => {
	try {
		if (url.startsWith('/')) return true
		if (!import.meta.client || typeof window === 'undefined') return false
		const parsed = new URL(url, window.location.origin)
		return parsed.origin === window.location.origin
	} catch {
		return false
	}
}
