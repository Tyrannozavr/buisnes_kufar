<template>
	<div class="max-w-full">
		<div class="bg-white shadow rounded-lg p-4 space-y-4">
			<div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
				<div class="flex flex-wrap gap-3 md:flex-row md:items-end">
					<div class="w-full md:w-48">
						<UFormField label="Закупки / Продажи">
							<USelect
								:model-value="dealTypeFilter"
								:items="DEAL_TYPE_OPTIONS"
								value-key="value"
								label-key="label"
								placeholder="Выберите"
								@update:model-value="handleSelectDealType"
							/>
						</UFormField>
					</div>
					<div class="w-full md:max-w-md">
						<UFormField label="Номер заказа">
							<USelect
								:model-value="selectedDealId"
								:items="orderOptions"
								value-key="value"
								label-key="label"
								placeholder="Выберите заказ"
								@update:model-value="handleSelectDeal"
							/>
						</UFormField>
					</div>
				</div>

				<UButton color="primary" icon="i-lucide-upload" :disabled="!selectedDealId" @click="handleOpenUploadModal">
					Загрузить документ
				</UButton>
			</div>

			<p v-if="isLoadingDocuments" class="text-sm text-neutral-500" role="status">
				Загрузка документов…
			</p>

			<UTable sticky :data="tableRows" :columns="columns" class="max-h-100 overflow-y-auto overscroll-auto" />
		</div>

		<UModal v-model:open="isUploadModalOpen" title="Загрузка документа">
			<template #body>
				<div class="space-y-4 p-4">
					<UFormField label="Тип документа">
						<USelect
							class="w-1/2"
							:model-value="uploadForm.documentType"
							:items="DOCUMENT_TYPE_OPTIONS"
							label-key="label"
							value-key="value"
							placeholder="Выберите тип документа"
							@update:model-value="handleSelectDocumentType"
						/>
					</UFormField>

					<UFormField label="Номер документа (необязательно)">
						<UInput class="w-1/2" v-model="uploadForm.documentNumber" placeholder="Например, INV-001" />
					</UFormField>

					<UFormField label="Файл">
						<div class="flex items-center gap-3">
							<UButton class="w-1/2" color="neutral" variant="outline" icon="i-lucide-file-up" @click="handleOpenFilePicker">
								Выбрать документ/скан
							</UButton>
							<span class="text-sm text-gray-600 truncate">
								{{ uploadForm.file?.name || "Файл не выбран" }}
							</span>
						</div>
						<input
							ref="fileInputRef"
							class="hidden"
							type="file"
							aria-label="Выберите файл документа"
							@change="handleFileChange"
						/>
					</UFormField>

					<div class="flex justify-end gap-2">
						<UButton color="neutral" variant="outline" :disabled="isUploading" @click="isUploadModalOpen = false">
							Отмена
						</UButton>
						<UButton color="primary" :loading="isUploading" :disabled="isUploadDisabled" @click="handleUploadDocument">
							Загрузить
						</UButton>
					</div>
				</div>
			</template>
		</UModal>

		<FileViewer
			v-model:isModalOpen="isFileViewerModalOpen"
			:deal-id="dataForFileViewer?.dealId ?? 0"
			:document-id="dataForFileViewer?.documentId ?? 0"
			:name="dataForFileViewer?.name"
			:type="dataForFileViewer?.type"
			@close="isFileViewerModalOpen = false"
		/>
	</div>
</template>

<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { useQuery, useQueryCache } from "@pinia/colada";
import { useDocumentsApi } from "~/api/documents";
import { uploadDocumentByIdQuery, deleteDocumentQuery } from "~/queries/documents";
import { buyerDealsQuery, sellerDealsQuery } from "~/queries/purchases";
import { QueryKeys } from "~/constants/queryKeys";
import {
	DEAL_TYPE_OPTIONS,
	DOCUMENT_TYPE_LABELS,
	DOCUMENT_TYPE_OPTIONS,
	type DealTypeFilter,
	type DocumentApiItem,
	type DocumentTableRow,
	type DocumentType,
	type OrderOption,
} from "~/types/documents";
import type { BuyerDealResponse, SellerDealResponse } from "~/types/dealResponse";
import type { Deal } from "~/types/dealState";
import { useDeals } from "~/composables/useDeals";
import { useDocxGenerator } from "~/composables/useDocxGenerator";
import { useRoute, useRouter } from "vue-router";
import FileViewer from "~/components/ui/File-viewer.vue";

definePageMeta({
	layout: "profile",
});

const BILL_SYNTHETIC_ID_OFFSET = 1_000_000;

/** Счёт в таблице только если счёт реально создан в сделке (есть дата и номер). */
const isBillCreatedInDeal = (deal: Deal): boolean => {
	const number = deal.bill?.number?.trim();
	const date = deal.billDate?.trim();
	return Boolean(number && date);
};

const toast = useToast();
const route = useRoute();
const router = useRouter();
const queryCache = useQueryCache();
const documentsApi = useDocumentsApi();
const UButton = resolveComponent("UButton");
const USelect = resolveComponent("USelect");
const UDropdownMenu = resolveComponent("UDropdownMenu");
const { findDeal, getDeals } = useDeals();
const { fetchDealGeneratedDocxBlob, downloadBlob } = useDocxGenerator();

const { uploadDocumentById } = uploadDocumentByIdQuery();
const { deleteDocument: deleteDocumentMutation } = deleteDocumentQuery();

const { data: buyerDealsRaw, state: buyerDealState } = useQuery(() => buyerDealsQuery({}));
const { data: sellerDealsRaw, state: sellerDealState } = useQuery(() => sellerDealsQuery({}));

const isDealsLoaded = computed(
	() =>
		buyerDealState.value.status !== "pending" &&
		sellerDealState.value.status !== "pending",
);

const buyerDeals = computed<(BuyerDealResponse | SellerDealResponse)[]>(() =>
	[...(buyerDealsRaw.value ?? [])].sort((a, b) => b.id - a.id),
);
const sellerDeals = computed<(BuyerDealResponse | SellerDealResponse)[]>(() =>
	[...(sellerDealsRaw.value ?? [])].sort((a, b) => b.id - a.id),
);

const dealTypeFilter = ref<DealTypeFilter>("purchases");
const selectedDealId = ref<number | null>(null);

const orderOptions = computed<OrderOption[]>(() => {
	const deals =
		dealTypeFilter.value === "purchases" ? buyerDeals.value : sellerDeals.value;

	return deals.map((deal) => {
		const orderNum =
			dealTypeFilter.value === "purchases"
				? deal.buyer_order_number
				: deal.seller_order_number;
		return {
			value: deal.id,
			orderNumber: orderNum,
			label: `№ ${orderNum}`,
		};
	});
});

const orderMap = computed(() => {
	const map: Record<number, string> = {};
	for (const deal of buyerDeals.value) {
		map[deal.id] = deal.buyer_order_number;
	}
	for (const deal of sellerDeals.value) {
		map[deal.id] = deal.seller_order_number;
	}
	return map;
});

const hasValidSelectedDeal = computed(() => {
	if (!selectedDealId.value) return false;
	return orderOptions.value.some((option) => option.value === selectedDealId.value);
});

const {
	data: documentsFromApi,
	error: documentsApiError,
	asyncStatus: documentsApiAsyncStatus,
} = useQuery({
	key: () => [QueryKeys.GET_DOCUMENTS_BY_DEAL_ID, selectedDealId.value ?? 0],
	query: async () => {
		const id = selectedDealId.value;
		if (id == null) return undefined;
		return useDocumentsApi().getDocumentsByDealId(id);
	},
	enabled: () =>
		isDealsLoaded.value &&
		selectedDealId.value != null &&
		hasValidSelectedDeal.value,
});

watch(documentsApiError, (err) => {
	if (!err) return;
	toast.add({
		title: "Ошибка",
		description: "Не удалось загрузить список документов",
		color: "error",
	});
});

const generatedDocuments = ref<DocumentApiItem[]>([]);
const isGeneratingDocs = ref(false);
const selectedDealFromStore = computed(() => {
	if (!selectedDealId.value) return null;
	return findDeal(selectedDealId.value) ?? null;
});

const createDocumentsFromState = async (dealId: number): Promise<DocumentApiItem[]> => {
	getDeals();
	const deal = findDeal(dealId);
	if (!deal) return [];

	const orderNumber =
		dealTypeFilter.value === "purchases"
			? deal.buyerOrderNumber
			: deal.sellerOrderNumber;

	const docs: DocumentApiItem[] = [];
	if (orderNumber) {
		try {
			const blob = await fetchDealGeneratedDocxBlob(deal.dealId, "order");
			docs.push({
				document_id: deal.dealId,
				deal_id: deal.dealId,
				document_type: "order",
				document_number: orderNumber ?? null,
				document_date: deal.date,
				document_file_path: null,
				created_at: deal.date,
				updated_at: deal.date,
				blob,
			});
		} catch (e) {
			if (import.meta.dev) console.error("fetch order.docx:", e);
		}
	}
	if (isBillCreatedInDeal(deal)) {
		try {
			const blob = await fetchDealGeneratedDocxBlob(deal.dealId, "bill");
			docs.push({
				document_id: deal.dealId + BILL_SYNTHETIC_ID_OFFSET,
				deal_id: deal.dealId,
				document_type: "bill",
				document_number: deal.bill.number ?? null,
				document_date: deal.date,
				document_file_path: null,
				created_at: deal.date,
				updated_at: deal.date,
				blob,
			});
		} catch (e) {
			if (import.meta.dev) console.error("fetch bill.docx:", e);
		}
	}
	return docs;
};

watch(
	[selectedDealId, dealTypeFilter, isDealsLoaded, hasValidSelectedDeal, selectedDealFromStore],
	async () => {
		if (!isDealsLoaded.value || !selectedDealId.value || !hasValidSelectedDeal.value) {
			generatedDocuments.value = [];
			return;
		}
		if (!selectedDealFromStore.value) {
			getDeals();
			generatedDocuments.value = [];
			return;
		}
		isGeneratingDocs.value = true;
		try {
			generatedDocuments.value = await createDocumentsFromState(selectedDealId.value);
		} finally {
			isGeneratingDocs.value = false;
		}
	},
	{ immediate: true },
);

const documents = computed<DocumentApiItem[]>(() => {
	if (!isDealsLoaded.value || !selectedDealId.value || !hasValidSelectedDeal.value) {
		return [];
	}
	return [...generatedDocuments.value, ...(documentsFromApi.value ?? [])];
});

const isLoadingDocuments = computed(
	() => documentsApiAsyncStatus.value === "loading" || isGeneratingDocs.value,
);

const getDocumentTypeLabel = (documentType: string): string => {
	return (
		DOCUMENT_TYPE_LABELS[documentType as keyof typeof DOCUMENT_TYPE_LABELS] ||
		documentType
	);
};

const getFileFormat = (path: string | null): string => {
	if (!path) return "-";
	const extension = path.split(".").pop();
	if (!extension) return "-";
	return extension.toUpperCase();
};

const tableRows = computed<DocumentTableRow[]>(() =>
	documents.value.map((item, index) => ({
		index: index + 1,
		id: item.document_id,
		dealId: item.deal_id,
		orderNumber: orderMap.value[item.deal_id] || `#${item.deal_id}`,
		documentNumber: item.document_number || `Документ #${item.document_id}`,
		documentType: getDocumentTypeLabel(item.document_type),
		format: getFileFormat(item.document_file_path),
		blob: item.blob,
	})),
);

watch(
	[buyerDeals, sellerDeals, dealTypeFilter],
	() => {
		const options =
			dealTypeFilter.value === "purchases" ? buyerDeals.value : sellerDeals.value;
		if (!options.length) return;
		const firstId = options[0]?.id ?? null;
		if (
			!selectedDealId.value ||
			!options.some((d) => d.id === selectedDealId.value)
		) {
			selectedDealId.value = firstId;
		}
	},
	{ flush: "post", immediate: true },
);

const isUploadModalOpen = ref(false);
const isUploading = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);
const dataForFileViewer = ref<{
	name: string;
	dealId: number;
	documentId: number;
	type: string;
} | null>(null);
const isFileViewerModalOpen = ref(false);

const uploadForm = reactive<{
	documentType: DocumentType | null;
	documentNumber: string;
	file: File | null;
}>({
	documentType: null,
	documentNumber: "",
	file: null,
});

const isUploadDisabled = computed(() => {
	if (!selectedDealId.value) return true;
	if (!uploadForm.documentType) return true;
	return !uploadForm.file;
});

const handleSelectDealType = (dealType: DealTypeFilter): void => {
	if (!dealType) return;
	dealTypeFilter.value = dealType;
	const currentOptions = orderOptions.value;

	const stillValid =
		selectedDealId.value &&
		currentOptions.some((o) => o.value === selectedDealId.value);

	if (!stillValid) {
		selectedDealId.value = currentOptions[0]?.value ?? null;
	}
};

const handleSelectDeal = (dealId: number): void => {
	selectedDealId.value = dealId;
};

const handleSelectDocumentType = (documentType: DocumentType): void => {
	uploadForm.documentType = documentType;
};

const invalidateDocumentsForDeal = (dealId: number): void => {
	queryCache.invalidateQueries({ key: [QueryKeys.GET_DOCUMENTS_BY_DEAL_ID, dealId] });
};

const handleOpenUploadModal = (): void => {
	uploadForm.documentType = DOCUMENT_TYPE_OPTIONS[0]?.value as DocumentType | null;
	uploadForm.documentNumber = "";
	uploadForm.file = null;
	isUploadModalOpen.value = true;
};

const handleOpenFilePicker = (): void => {
	fileInputRef.value?.click();
};

const handleFileChange = (event: Event): void => {
	const target = event.target as HTMLInputElement;
	const selectedFile = target.files?.[0];
	uploadForm.file = selectedFile || null;
};

const handleUploadDocument = async (): Promise<void> => {
	if (!selectedDealId.value || !uploadForm.documentType || !uploadForm.file) return;

	const formData = new FormData();
	formData.append("file", uploadForm.file);
	formData.append("document_type", uploadForm.documentType);

	if (uploadForm.documentNumber.trim()) {
		formData.append("document_number", uploadForm.documentNumber.trim());
	}

	const dealId = selectedDealId.value;
	isUploading.value = true;
	try {
		await uploadDocumentById(dealId, formData);

		toast.add({
			title: "Успешно",
			description: "Документ загружен",
			color: "success",
		});

		isUploadModalOpen.value = false;
		invalidateDocumentsForDeal(dealId);
	} catch (error) {
		toast.add({
			title: "Ошибка",
			description: "Не удалось загрузить документ",
			color: "error",
		});
		if (import.meta.dev) console.error("upload document:", error);
	} finally {
		isUploading.value = false;
	}
};

const handleDownloadDocument = async (row: DocumentTableRow): Promise<void> => {
	if (!selectedDealId.value) return;

	try {
		const result = await documentsApi.downloadDocument(
			selectedDealId.value,
			row.id,
			true,
		);

		if (result instanceof Blob) {
			const url = URL.createObjectURL(result);
			const a = document.createElement("a");
			a.href = url;
			a.download = `document-${row.orderNumber}`;
			a.click();
			URL.revokeObjectURL(url);
		} else if (result?.url) {
			window.open(result.url, "_blank", "noopener,noreferrer");
		} else {
			throw new Error("Не удалось получить файл");
		}
	} catch (error) {
		toast.add({
			title: "Ошибка",
			description: "Не удалось скачать документ",
			color: "error",
		});
		if (import.meta.dev) console.error("download document:", error);
	}
};

const handleDeleteDocument = async (row: DocumentTableRow): Promise<void> => {
	if (!selectedDealId.value) return;

	const dealId = selectedDealId.value;
	try {
		await deleteDocumentMutation(dealId, row.id);
		toast.add({
			title: "Успешно",
			description: "Документ удален",
			color: "success",
		});
		invalidateDocumentsForDeal(dealId);
	} catch (error) {
		toast.add({
			title: "Ошибка",
			description: "Не удалось удалить документ",
			color: "error",
		});
		if (import.meta.dev) console.error("delete document:", error);
	}
};

const handleDeleteDocumentWithBlob = (): void => {
	toast.add({
		title: "Ой!",
		description: "Удаление документов, созданных из таблицы пока не реализовано",
		color: "info",
	});
};

const columns: TableColumn<DocumentTableRow>[] = [
	{ accessorKey: "index", header: "п/п" },
	{ accessorKey: "orderNumber", header: "№ заказа" },
	{ accessorKey: "documentNumber", header: "№ документа" },
	{ accessorKey: "documentType", header: "Тип документа" },
	{ accessorKey: "format", header: "Формат" },
	{
		id: "actions",
		meta: {
			class: {
				td: "flex justify-end",
			},
		},
		cell: ({ row }) => {
			const rowData = row.original;
			return h(UDropdownMenu, {
				items: [
					{
						label: "Скачать",
						icon: "i-lucide-download",
						color: "primary",
						variant: "soft",
						onClick: () =>
							rowData.blob
								? downloadBlob(rowData.blob, `document-${rowData.orderNumber}`)
								: handleDownloadDocument(rowData),
					},
					{
						label: "Удалить",
						icon: "i-lucide-trash-2",
						color: "error",
						variant: "soft",
						onClick: () =>
							rowData.blob ? handleDeleteDocumentWithBlob() : handleDeleteDocument(rowData),
					},
					{
						label: "Просмотр",
						icon: "i-lucide-eye",
						onClick: () => {
							if (rowData.format === "-") {
								router.push({
									path: "/profile/editor",
									query: {
										dealId: rowData.dealId,
										role: dealTypeFilter.value === "purchases" ? "buyer" : "seller",
									},
								});
								return;
							}
							isFileViewerModalOpen.value = true;
							dataForFileViewer.value = {
								dealId: rowData.dealId,
								documentId: rowData.id,
								type: rowData.format.toLowerCase(),
								name: rowData.documentNumber,
							};
						},
					},
				],
				"aria-label": "Действия с документом",
			}, () =>
				h(UButton, {
					icon: "i-lucide-ellipsis",
					size: "xs",
					color: "neutral",
					variant: "soft",
					"aria-label": "Действия с документом",
				}),
			);
		},
	},
];

watch(
	() => route.query,
	() => {
		if (!route.query.dealId) return;
		const parsedDealId = Number(route.query.dealId);
		if (Number.isNaN(parsedDealId) || parsedDealId <= 0) return;
		if (!selectedDealId.value || selectedDealId.value !== parsedDealId) {
			selectedDealId.value = parsedDealId;
		}
	},
	{ immediate: true },
);

watch(
	() => selectedDealId.value,
	() => {
		if (isDealsLoaded.value && selectedDealId.value && hasValidSelectedDeal.value) {
			router.replace({
				query: { ...route.query, dealId: selectedDealId.value.toString() },
			});
		}
	},
);
</script>
