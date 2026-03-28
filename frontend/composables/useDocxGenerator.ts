import { useNuxtApp } from "nuxt/app";
import { API_URLS } from "~/constants/urls";
import { normalizeApiPath } from "~/utils/normalize";

export type DealGeneratedDocxVariant =
	| "order"
	| "bill"
	| "bill-contract"
	| "bill-offer";

const variantToApiPath = (
	dealId: number,
	variant: DealGeneratedDocxVariant
): string => {
	switch (variant) {
		case "order":
			return API_URLS.DOWNLOAD_DEAL_DOCX_ORDER(dealId);
		case "bill":
			return API_URLS.DOWNLOAD_DEAL_DOCX_BILL(dealId);
		case "bill-contract":
			return API_URLS.DOWNLOAD_DEAL_DOCX_BILL_CONTRACT(dealId);
		case "bill-offer":
			return API_URLS.DOWNLOAD_DEAL_DOCX_BILL_OFFER(dealId);
	}
};

const variantToPdfApiPath = (
	dealId: number,
	variant: DealGeneratedDocxVariant
): string => {
	switch (variant) {
		case "order":
			return API_URLS.DOWNLOAD_DEAL_PDF_ORDER(dealId);
		case "bill":
			return API_URLS.DOWNLOAD_DEAL_PDF_BILL(dealId);
		case "bill-contract":
			return API_URLS.DOWNLOAD_DEAL_PDF_BILL_CONTRACT(dealId);
		case "bill-offer":
			return API_URLS.DOWNLOAD_DEAL_PDF_BILL_OFFER(dealId);
	}
};

export const useDocxGenerator = () => {
	const ensureClient = () => {
		if (import.meta.server) {
			throw new Error("useDocxGenerator is client-only (SSR disabled for this feature)");
		}
	};

	const downloadBlob = (blob: Blob, fileName: string): void => {
		ensureClient();
		const url = URL.createObjectURL(blob);
		const link = document.createElement("a");
		link.href = url;
		link.download = fileName;
		link.click();
		URL.revokeObjectURL(url);
	};

	/** GET с авторизацией как у остального API; ответ — бинарный .docx */
	const fetchDealGeneratedDocxBlob = async (
		dealId: number,
		variant: DealGeneratedDocxVariant
	): Promise<Blob> => {
		ensureClient();
		const { $api } = useNuxtApp();
		const path = normalizeApiPath(variantToApiPath(dealId, variant));
		return (await $api.get(path, {
			responseType: "blob",
			headers: {
				Accept:
					"application/vnd.openxmlformats-officedocument.wordprocessingml.document, */*",
			},
		})) as Blob;
	};

	const downloadDealGeneratedDocx = async (
		dealId: number,
		variant: DealGeneratedDocxVariant,
		fileName?: string
	): Promise<void> => {
		const blob = await fetchDealGeneratedDocxBlob(dealId, variant);
		const defaultName = `${variant}-deal-${dealId}.docx`;
		downloadBlob(blob, fileName ?? defaultName);
	};

	const fetchDealGeneratedPdfBlob = async (
		dealId: number,
		variant: DealGeneratedDocxVariant
	): Promise<Blob> => {
		ensureClient();
		const { $api } = useNuxtApp();
		const path = normalizeApiPath(variantToPdfApiPath(dealId, variant));
		return (await $api.get(path, {
			responseType: "blob",
			headers: { Accept: "application/pdf, */*" },
		})) as Blob;
	};

	const downloadDealGeneratedPdf = async (
		dealId: number,
		variant: DealGeneratedDocxVariant,
		fileName?: string
	): Promise<void> => {
		const blob = await fetchDealGeneratedPdfBlob(dealId, variant);
		const defaultName = `${variant}-deal-${dealId}.pdf`;
		downloadBlob(blob, fileName ?? defaultName);
	};

	return {
		fetchDealGeneratedDocxBlob,
		downloadDealGeneratedDocx,
		fetchDealGeneratedPdfBlob,
		downloadDealGeneratedPdf,
		downloadBlob,
	};
};
