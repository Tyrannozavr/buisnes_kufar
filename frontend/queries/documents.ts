import { defineMutation, defineQueryOptions, useMutation } from "@pinia/colada";
import { useDocumentsApi } from "~/api/documents";
import { QueryKeys } from "~/constants/queryKeys";

export const getDocumentsByDealIdQuery = defineQueryOptions(({ dealId }: { dealId: number }) => ({
	key: [QueryKeys.GET_DOCUMENTS_BY_DEAL_ID, dealId],
	query: () => useDocumentsApi().getDocumentsByDealId(dealId),
}))

export const uploadDocumentByIdQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.UPLOAD_DOCUMENT_BY_DEAL_ID],
		mutation: ({ dealId, formData }: { dealId: number, formData: FormData }) => useDocumentsApi().uploadDocumentById(dealId, formData),
	})

	return {
		...mutation,
		uploadDocumentById: (dealId: number, formData: FormData) => mutate({ dealId, formData }),
	}
})

export const downloadDocumentQuery = defineQueryOptions(({ dealId, documentId }: { dealId: number, documentId: number }) => ({
	key: [QueryKeys.DOWNLOAD_DOCUMENT, dealId, documentId],
	query: () => useDocumentsApi().downloadDocument(dealId, documentId),
}))

export const deleteDocumentQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.DELETE_DOCUMENT_BY_DEAL_ID],
		mutation: ({ dealId, documentId }: { dealId: number, documentId: number }) => useDocumentsApi().deleteDocument(dealId, documentId),
	})

	return {
		...mutation,
		deleteDocument: (dealId: number, documentId: number) => mutate({ dealId, documentId }),
	}
})
