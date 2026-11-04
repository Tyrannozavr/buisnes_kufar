import { formatDocumentLinkLabel } from './normalize'
import {
	TRANSPORT_DOCUMENT_SHORT_LABELS,
	TRANSPORT_DOCUMENT_TYPES,
	type TransportContractSnapshot,
	type TransportContractSnapshotDoc,
	type TransportDocumentType,
} from '../types/transportDocument'

function asType(raw?: string): TransportDocumentType | null {
	if (!raw) return null
	if (raw === 'transport_expedition') return 'expedition_contract'
	return (TRANSPORT_DOCUMENT_TYPES as readonly string[]).includes(raw)
		? (raw as TransportDocumentType)
		: null
}

/** Полное юрлицо → короткий вид для таблицы/селекта. */
export function shortenOrgName(name: string): string {
	const raw = name.trim()
	if (!raw) return raw
	return raw
		.replace(/^Общество с ограниченной ответственностью\s+/i, 'ООО ')
		.replace(/^Акционерное общество\s+/i, 'АО ')
		.replace(/^Публичное акционерное общество\s+/i, 'ПАО ')
		.replace(/^Индивидуальный предприниматель\s+/i, 'ИП ')
		.replace(/\s+/g, ' ')
		.trim()
}

function lineForDoc(doc: TransportContractSnapshotDoc): string | null {
	const t = asType(doc.type)
	if (!t || !doc.number) return null
	const rawDate = doc.date ? String(doc.date).slice(0, 10) : ''
	const core = formatDocumentLinkLabel(String(doc.number), rawDate)
	if (!core) return null
	return `${TRANSPORT_DOCUMENT_SHORT_LABELS[t]} № ${core}`
}

function snapshotDocs(snapshot: TransportContractSnapshot): TransportContractSnapshotDoc[] {
	if (!snapshot) return []
	if (snapshot.documents?.length) return snapshot.documents
	if (snapshot.number) {
		return [
			{
				type: snapshot.type,
				number: snapshot.number,
				date: snapshot.date,
				carrier_name: snapshot.carrier_name,
			},
		]
	}
	return []
}

function carrierFromSnapshot(snapshot: TransportContractSnapshot): string | null {
	if (!snapshot) return null
	const docs = snapshotDocs(snapshot)
	const carrier =
		snapshot.carrier_name?.trim() ||
		docs.find((d) => d.carrier_name?.trim())?.carrier_name?.trim()
	return carrier ? shortenOrgName(carrier) : null
}

/**
 * Строки для ячейки «Договор перевозки» (§1.4 / B.1).
 * Каждый документ — отдельная кликабельная строка.
 */
export function buildTransportCellLines(
	snapshot: TransportContractSnapshot,
): string[] {
	return buildTransportDocEntries(snapshot).map((e) => e.label)
}

export type TransportDocCellEntry = {
	label: string
	id?: number
	type?: string
}

/** Документы snapshot по одному (для отдельных кнопок в таблице). */
export function buildTransportDocEntries(
	snapshot: TransportContractSnapshot,
): TransportDocCellEntry[] {
	if (!snapshot) return []
	const entries: TransportDocCellEntry[] = []
	const seen = new Set<string>()
	for (const doc of snapshotDocs(snapshot)) {
		const line = lineForDoc(doc)
		if (!line || seen.has(line)) continue
		seen.add(line)
		entries.push({
			label: line,
			id: doc.id ? Number(doc.id) : undefined,
			type: doc.type,
		})
	}
	return entries
}

/** Полный текст для title/tooltip (каждая сущность с новой строки). */
export function buildTransportCellTooltip(
	snapshot: TransportContractSnapshot,
): string {
	if (!snapshot) return ''
	const lines: string[] = []
	const seen = new Set<string>()
	for (const doc of snapshotDocs(snapshot)) {
		const line = lineForDoc(doc)
		if (line && !seen.has(line)) {
			seen.add(line)
			lines.push(line)
		}
	}
	const carrier = carrierFromSnapshot(snapshot)
	if (carrier) lines.push(carrier)
	return lines.join('\n')
}

/** Первый документ для открытия в редакторе. */
export function primaryTransportDocId(
	snapshot: TransportContractSnapshot,
): number | null {
	const docs = snapshot?.documents ?? []
	for (const d of docs) {
		if (d.id) return d.id
	}
	return null
}
