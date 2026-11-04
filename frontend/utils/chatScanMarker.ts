/** Маркер вложения-скана сделки в тексте чата — без второй загрузки файла. */

export type ChatScanRef = {
	dealId: number
	documentId: number
	filename: string
}

const SCAN_MARKER_RE =
	/\[\[scan:deal=(\d+);doc=(\d+);name=([^\]]+)\]\]/g

export function buildChatScanMarker(
	dealId: number,
	documentId: number,
	filename: string,
): string {
	const safeName = String(filename || 'file')
		.replace(/[\[\];]/g, '_')
		.slice(0, 120)
	return `[[scan:deal=${dealId};doc=${documentId};name=${safeName}]]`
}

/** Не больше одного превью на сообщение — иначе N параллельных download. */
const MAX_SCAN_REFS_PER_MESSAGE = 1

export function extractChatScanRefs(content: string): ChatScanRef[] {
	const refs: ChatScanRef[] = []
	const re = new RegExp(SCAN_MARKER_RE.source, 'g')
	let match: RegExpExecArray | null
	while ((match = re.exec(content)) !== null) {
		refs.push({
			dealId: Number(match[1]),
			documentId: Number(match[2]),
			filename: match[3] || 'file',
		})
		if (refs.length >= MAX_SCAN_REFS_PER_MESSAGE) break
	}
	return refs
}

export function stripChatScanMarkers(content: string): string {
	return content.replace(new RegExp(SCAN_MARKER_RE.source, 'g'), '').trim()
}
