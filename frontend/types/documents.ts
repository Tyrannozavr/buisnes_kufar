export type DocumentTypeCode =
  | "order"
  | "bill"
  | "supply_contract"
  | "contract"
  | "other";

export interface DocumentApiItem {
  document_id: number;
  deal_id: number;
  document_type: DocumentTypeCode | string;
  document_number: string | null;
  document_date: string | null;
  document_file_path: string | null;
  created_at: string;
  updated_at: string;
  blob?: Blob;
}

export interface DocumentUploadResponse {
  message: string;
  document_id: number;
}

export interface DocumentDownloadResponse {
  url: string;
}

export interface OrderOption {
  label: string;
  value: number;
  orderNumber: string;
}

export interface DocumentTableRow {
  id: number;
  index: number;
  dealId: number;
  orderNumber: string;
  documentNumber: string;
  documentType: string;
  format: string;
  blob?: Blob;
}

export const DOCUMENT_TYPE_OPTIONS: { label: string; value: DocumentTypeCode }[] = [
  { label: "Заказ", value: "order" },
  { label: "Счет", value: "bill" },
  { label: "Договор поставки", value: "supply_contract" },
  { label: "Контракт", value: "contract" },
  { label: "Другие документы", value: "other" },
];

export const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  order: "Заказ",
  bill: "Счет",
  supply_contract: "Договор поставки",
  contract: "Контракт",
  other: "Другие документы",
};

export type DealTypeFilter = "purchases" | "sales";

export const DEAL_TYPE_OPTIONS: { label: string; value: DealTypeFilter }[] = [
  { label: "Закупки", value: "purchases" },
  { label: "Продажи", value: "sales" },
];
