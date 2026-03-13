export type DocumentTypeResponse =
	| "order"
	| "bill"
	| "supply_contract"
	| "contract"
	| "other"
	| "act"

export type DocumentType =
	| "order"
	| "bill"
	| "supplyContract"
	| "contract"
	| "other"
	| "act"

export const DOCUMENT_TYPE_MAP: Record<DocumentType, DocumentTypeResponse> = {
	order: "order",
	bill: "bill",
	supplyContract: "supply_contract",
	contract: "contract",
	act: "act",
	other: "other"
}

export interface DocumentFormResponse {
	payload?: Record<string, number | string>
	updated_by_company_id?: number | null
	updated_at?: string | null
}

export interface DocumentApiItem {
	document_id: number
	deal_id: number
	document_type: DocumentType
	document_number: string | null
	document_date: string | null
	document_file_path: string | null
	created_at: string
	updated_at: string
	blob?: Blob
}

export interface DocumentUploadResponse {
	message: string
	document_id: number
}

export interface DocumentDownloadResponse {
	url: string
}

export interface OrderOption {
	label: string
	value: number
	orderNumber: string
}

export interface DocumentTableRow {
	id: number
	index: number
	dealId: number
	orderNumber: string
	documentNumber: string
	documentType: string
	format: string
	blob?: Blob
}

export const DOCUMENT_TYPE_OPTIONS: {
	label: string
	value: DocumentTypeResponse
}[] = [
	{ label: "Заказ", value: "order" },
	{ label: "Счет", value: "bill" },
	{ label: "Договор поставки", value: "supply_contract" },
	{ label: "Контракт", value: "contract" },
	{ label: "Другие документы", value: "other" }
]

export const DOCUMENT_TYPE_LABELS: Record<DocumentTypeResponse, string> = {
	order: "Заказ",
	bill: "Счет",
	supply_contract: "Договор поставки",
	contract: "Контракт",
	other: "Другие документы",
	act: "Акт"
}

export type DealTypeFilter = "purchases" | "sales"

export const DEAL_TYPE_OPTIONS: { label: string; value: DealTypeFilter }[] = [
	{ label: "Закупки", value: "purchases" },
	{ label: "Продажи", value: "sales" }
]
