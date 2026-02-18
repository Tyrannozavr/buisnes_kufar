import { API_URLS } from "~/constants/urls";
import { normalizeApiPath } from "~/utils/normalize";
import { useNuxtApp } from "nuxt/app";
import type {
  DocumentApiItem,
  DocumentDownloadResponse,
  DocumentUploadResponse,
} from "~/types/documents";

export const useDocumentsApi = () => {
  const { $api } = useNuxtApp();
  
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
    getDocumentsByDealId,
    uploadDocumentById,
    downloadDocument,
    deleteDocument,
  };
};
