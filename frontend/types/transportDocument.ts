/** Семь типов ТЗ «Договор на перевозку грузов». */

export const TRANSPORT_DOCUMENT_TYPES = [
	'carriage_contract',
	'carriage_application',
	'carriage_order',
	'expedition_contract',
	'forwarder_assignment',
	'forwarder_receipt',
	'warehouse_receipt',
] as const

export type TransportDocumentType = (typeof TRANSPORT_DOCUMENT_TYPES)[number]

export const TRANSPORT_DOCUMENT_TYPE_LABELS: Record<TransportDocumentType, string> = {
	carriage_contract: 'Договор на перевозку грузов',
	carriage_application: 'Заявка к договору на перевозку грузов',
	carriage_order: 'Договор-заявка',
	expedition_contract: 'Договор транспортной экспедиции',
	forwarder_assignment: 'Поручение экспедитору',
	forwarder_receipt: 'Экспедиторская расписка',
	warehouse_receipt: 'Складская расписка',
}

/** Короткие подписи для ячейки таблицы. */
export const TRANSPORT_DOCUMENT_SHORT_LABELS: Record<TransportDocumentType, string> = {
	carriage_contract: 'Договор перевозки',
	carriage_application: 'Заявка',
	carriage_order: 'Договор-заявка',
	expedition_contract: 'Договор транспортной экспедиции',
	forwarder_assignment: 'Поручение',
	forwarder_receipt: 'Эксп. расписка',
	warehouse_receipt: 'Склад. расписка',
}

export const TRANSPORT_FRAMEWORK_TYPES: readonly TransportDocumentType[] = [
	'carriage_contract',
	'expedition_contract',
] as const

export const TRANSPORT_CHILD_PARENT: Partial<
	Record<TransportDocumentType, TransportDocumentType>
> = {
	carriage_application: 'carriage_contract',
	forwarder_assignment: 'expedition_contract',
	forwarder_receipt: 'expedition_contract',
	warehouse_receipt: 'expedition_contract',
}

export type TransportDocumentItem = {
	id: number
	owner_company_id: number
	carrier_company_id: number
	carrier_name?: string
	doc_type: TransportDocumentType | string
	number: string
	date: string
	parent_id?: number | null
	deal_id?: number | null
	/** Бланк договора перевозки (§2) — преамбула, тело, реквизиты. */
	payload_json?: Record<string, unknown> | null
}

export type TransportDocumentUpdatePayload = {
	number?: string
	date?: string
	payload_json?: Record<string, unknown> | null
}

export type TransportDocumentListResponse = {
	documents: TransportDocumentItem[]
}

/** Снимок в orders.transport_contract (dual-write §1.2). */
export type TransportContractSnapshotDoc = {
	id?: number
	type?: string
	number?: string
	date?: string
	carrier_company_id?: number
	carrier_name?: string
	parent_id?: number | null
}

export type TransportContractSnapshot = {
	number?: string
	date?: string
	type?: string
	carrier_company_id?: number
	carrier_name?: string
	documents?: TransportContractSnapshotDoc[]
} | null
