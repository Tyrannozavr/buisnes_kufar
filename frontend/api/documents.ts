import { API_URLS } from "~/constants/urls";
import { normalizeApiPath } from "~/utils/normalize";
import { useNuxtApp } from "nuxt/app";
import type {
  DocumentApiItem,
  DocumentDownloadResponse,
  DocumentUploadResponse,
} from "~/types/documents";

/** Маппинг слотов вкладок редактора на тип документа для API getDocument/saveDocument. */
export const SLOT_TO_DOCUMENT_TYPE: Record<
  string,
  "order" | "bill" | "supply_contract" | "contract" | "other"
> = {
  order: "order",
  bill: "bill",
  supplyContract: "supply_contract",
  accompanyingDocuments: "other",
  invoice: "other",
  contract: "contract",
  act: "other",
  othersDocument: "other",
};

export type DocumentType =
  (typeof SLOT_TO_DOCUMENT_TYPE)[keyof typeof SLOT_TO_DOCUMENT_TYPE];

export interface DocumentFormResponse {
  payload?: Record<string, unknown>;
  document_version?: string;
  updated_by_company_id?: number | null;
  updated_at?: string | null;
}

export const useDocumentsApi = () => {
  const { $api } = useNuxtApp();

  /** Получение payload формы документа по сделке и типу (GET /deals/{id}/documents/form). */
  const getDocument = async (
    dealId: number,
    documentType: string,
    version?: string,
  ): Promise<DocumentFormResponse> => {
    const url = normalizeApiPath(
      API_URLS.GET_DOCUMENT_FORM(dealId, documentType) +
        (version ? `&version=${encodeURIComponent(version)}` : ""),
    );
    const response = await $api.get(url);
    return response as DocumentFormResponse;
  };

  /** Сохранение payload формы документа (PUT /deals/{id}/documents/form). Версионирование: version опционально (v1, v1.1). */
  const saveDocument = async (
    dealId: number,
    documentType: string,
    payload: Record<string, unknown>,
    version?: string,
  ): Promise<DocumentFormResponse> => {
    const url = normalizeApiPath(API_URLS.PUT_DOCUMENT_FORM(dealId));
    const body = { document_type: documentType, payload, ...(version ? { version } : {}) };
    const response = await $api.put(url, body);
    return response as DocumentFormResponse;
  };

  const getDocumentsByDealId = async (
    deal_id: number,
  ): Promise<DocumentApiItem[] | undefined> => {
    try {
      const response = await $api.get(
        normalizeApiPath(API_URLS.GET_DOCUMENTS_BY_DEAL_ID(deal_id)),
      );
      return response;
    } catch (error) {
      console.log("ERROR: ", error);
    }
  };

  const uploadDocumentById = async (deal_id: number, formData?: FormData) => {
    try {
      const response = await $api.post(
        normalizeApiPath(API_URLS.UPLOAD_DOCUMENT_BY_DEAL_ID(deal_id)),
        formData ?? {},
      );
      return response as DocumentUploadResponse;
    } catch (error) {
      console.error("ERROR uploadDocumentById:", error);
      throw error;
    }
  };

  const downloadDocument = async (
    deal_id: number,
    document_id: number,
    stream = true,
  ): Promise<DocumentDownloadResponse | Blob | undefined> => {
    try {
      if (stream) {
        const blob = await $api.get(
          normalizeApiPath(API_URLS.DOWNLOAD_DOCUMENT(deal_id, document_id)),
          { query: { stream: true }, responseType: "blob" },
        );
        return blob as Blob;
      }
      const response = await $api.get(
        normalizeApiPath(API_URLS.DOWNLOAD_DOCUMENT(deal_id, document_id)),
        { query: { redirect: false } },
      );
      return response as DocumentDownloadResponse;
    } catch (error) {
      console.error("ERROR downloadDocument:", error);
      throw error;
    }
  };

  const deleteDocument = async (deal_id: number, document_id: number) => {
    try {
      const response = await $api.delete(
        normalizeApiPath(API_URLS.DELETE_DOCUMENT(deal_id, document_id)),
      );
      return response;
    } catch (error) {
      console.log("ERROR: ", error);
    }
  };

  return {
    getDocument,
    saveDocument,
    getDocumentsByDealId,
    uploadDocumentById,
    downloadDocument,
    deleteDocument,
  };
};
