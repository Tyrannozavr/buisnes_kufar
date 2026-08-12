<template>
	<div class="max-w-full space-y-4">
		<div class="bg-white shadow rounded-lg p-4 space-y-4">
			<div class="space-y-3">
				<div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
					<div class="min-w-0 flex-1">
						<UFormField label="Контрагент">
							<USelect
								class="w-full"
								:model-value="counterpartyFilterId"
								:items="counterpartyOptions"
								value-key="value"
								label-key="label"
								placeholder="Все контрагенты"
								@update:model-value="handleSelectCounterparty"
							/>
						</UFormField>
					</div>
					<UButton
						class="shrink-0"
						color="primary"
						icon="i-lucide-upload"
						:disabled="!selectedDealId"
						@click="handleOpenUploadModal"
					>
						Загрузить документ
					</UButton>
				</div>

				<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
					<UFormField label="Тип документа">
						<USelect
							class="w-full"
							v-model="typeFilter"
							:items="TYPE_FILTER_OPTIONS"
							value-key="value"
							label-key="label"
							placeholder="Все типы"
						/>
					</UFormField>
					<UFormField label="Период с">
						<UInput class="w-full" v-model="dateFrom" type="date" />
					</UFormField>
					<UFormField label="Период по">
						<UInput class="w-full" v-model="dateTo" type="date" />
					</UFormField>
					<UFormField label="Закупки / Продажи">
						<USelect
							class="w-full"
							:model-value="dealTypeFilter"
							:items="DEAL_TYPE_OPTIONS"
							value-key="value"
							label-key="label"
							placeholder="Выберите"
							@update:model-value="handleSelectDealType"
						/>
					</UFormField>
				</div>

				<div class="max-w-xl">
					<UFormField label="Номер заказа">
						<USelect
							class="w-full"
							:model-value="selectedDealId"
							:items="orderSelectItems"
							value-key="value"
							label-key="label"
							placeholder="Выберите заказ"
							:disabled="!orderOptions.length"
							@update:model-value="handleSelectDeal"
						/>
					</UFormField>
					<p v-if="!orderOptions.length" class="text-xs text-neutral-500 mt-1">
						{{ emptyOrdersHint }}
					</p>
				</div>
			</div>

			<p
				v-if="counterpartyFilterId && orderOptions.length"
				class="text-sm text-amber-800 bg-amber-50 border border-amber-100 rounded px-3 py-2"
			>
				{{
					selectedDealId
						? "Документы выбранного заказа и договоры ЛК с этим контрагентом."
						: "Документы всех заказов по фильтру и договоры ЛК с этим контрагентом."
				}}
			</p>
			<p
				v-else-if="!counterpartyFilterId && orderOptions.length && !selectedDealId"
				class="text-sm text-neutral-600 bg-neutral-50 border border-neutral-100 rounded px-3 py-2"
			>
				Показаны документы всех заказов в режиме «Продажи/Закупки». Договоры — после выбора контрагента.
			</p>
			<p
				v-else-if="!counterpartyFilterId && selectedDealId"
				class="text-sm text-neutral-600 bg-neutral-50 border border-neutral-100 rounded px-3 py-2"
			>
				Показаны документы выбранного заказа. Чтобы увидеть договоры — выберите контрагента.
			</p>
			<p
				v-else-if="counterpartyFilterId && !orderOptions.length && hasOrdersOnOtherSide"
				class="text-sm text-amber-800 bg-amber-50 border border-amber-100 rounded px-3 py-2"
			>
				В этом режиме заказов нет — таблица пуста. Переключите «Закупки / Продажи», чтобы увидеть заказы и договоры.
			</p>

			<p v-if="isLoadingDocuments" class="text-sm text-neutral-500" role="status">
				Загрузка документов…
			</p>

			<UTable sticky :data="unifiedTableRows" :columns="columns" class="max-h-100 overflow-y-auto overscroll-auto" />
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
								{{ uploadFile?.name || "Файл не выбран" }}
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

	<ConfirmDeleteModal
		v-model:open="deleteOpen"
		:title="deleteTitle"
		:message="deleteMessage"
		:loading="deleteLoading"
		@confirm="confirmDelete"
	/>
</template>

<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { useQuery, useQueryCache } from "@pinia/colada";
import { useDocumentsApi } from "~/api/documents";
import { getCounterparties } from "~/api/company";
import { usePurchasesApi } from "~/api/purchases";
import { uploadDocumentByIdQuery, deleteDocumentQuery } from "~/queries/documents";
import { buyerDealsQuery, sellerDealsQuery } from "~/queries/purchases";
import { QueryKeys } from "~/constants/queryKeys";
import type { CompanyContractItem } from "~/types/companyContract";
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
import { normalizeDate } from "~/utils/normalize";

definePageMeta({
	layout: "profile",
	ssr: false,
});

const BILL_SYNTHETIC_ID_OFFSET = 1_000_000;

const {
	deleteOpen,
	deleteLoading,
	deleteTitle,
	deleteMessage,
	askDelete,
	confirmDelete,
} = useConfirmDelete();

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
const { findDeal, getDeals, ensureDealLoaded } = useDeals();
const { fetchDealGeneratedDocxBlob, downloadBlob } = useDocxGenerator();

const { uploadDocumentById } = uploadDocumentByIdQuery();
const { deleteDocumentAsync } = deleteDocumentQuery();

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
const counterpartyFilterId = ref<number | null>(null)
const typeFilter = ref<string>("all")
const dateFrom = ref("")
const dateTo = ref("")
const companyContracts = ref<CompanyContractItem[]>([])
const purchasesApi = usePurchasesApi()

const TYPE_FILTER_OPTIONS = [
	{ label: "Все типы", value: "all" },
	{ label: "Договор (ЛК)", value: "company_contract" },
	...DOCUMENT_TYPE_OPTIONS.map((o) => ({ label: o.label, value: o.value })),
]

const { data: counterpartiesList } = await getCounterparties(1, 100)
const counterpartyOptions = computed(() => [
	{ label: "Все контрагенты", value: null as number | null },
	...(counterpartiesList.value ?? []).map((c) => ({
		label: c.fullName || c.slug,
		value: c.id as number | null,
	})),
])

const dealMatchesCounterparty = (deal: BuyerDealResponse | SellerDealResponse): boolean => {
	if (!counterpartyFilterId.value) return true
	const id = counterpartyFilterId.value
	return deal.buyer_company_id === id || deal.seller_company_id === id
}

const salesOrdersForFilter = computed(() =>
	sellerDeals.value.filter(dealMatchesCounterparty),
)
const purchaseOrdersForFilter = computed(() =>
	buyerDeals.value.filter(dealMatchesCounterparty),
)

const orderOptions = computed<OrderOption[]>(() => {
	const deals =
		dealTypeFilter.value === "purchases"
			? purchaseOrdersForFilter.value
			: salesOrdersForFilter.value

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

const orderSelectItems = computed(() => {
	if (!orderOptions.value.length) {
		return [{ label: "Нет заказов", value: null as number | null, orderNumber: "" }]
	}
	return [
		{ label: "Все заказы", value: null as number | null, orderNumber: "" },
		...orderOptions.value,
	]
})

const emptyOrdersHint = computed(() => {
	if (orderOptions.value.length) return ""
	if (counterpartyFilterId.value) {
		return dealTypeFilter.value === "purchases"
			? "С этим контрагентом нет заказов в закупках — переключите на «Продажи»."
			: "С этим контрагентом нет заказов в продажах — переключите на «Закупки»."
	}
	return dealTypeFilter.value === "purchases"
		? "Нет заказов в закупках."
		: "Нет заказов в продажах."
})

const hasOrdersOnOtherSide = computed(() => {
	if (orderOptions.value.length) return false
	return dealTypeFilter.value === "purchases"
		? salesOrdersForFilter.value.length > 0
		: purchaseOrdersForFilter.value.length > 0
})

/** Подставить Продажи/Закупки, где реально есть заказы (после загрузки сделок). */
const preferDealTypeWithOrders = () => {
	if (!isDealsLoaded.value) return
	const salesN = salesOrdersForFilter.value.length
	const buyN = purchaseOrdersForFilter.value.length
	if (buyN === 0 && salesN > 0) dealTypeFilter.value = "sales"
	else if (salesN === 0 && buyN > 0) dealTypeFilter.value = "purchases"
}

const loadContracts = async () => {
	try {
		const res = await purchasesApi.getCompanyContracts(
			counterpartyFilterId.value ?? undefined,
		)
		companyContracts.value = res?.contracts ?? []
	} catch {
		companyContracts.value = []
	}
}

watch(
	counterpartyFilterId,
	() => {
		void loadContracts()
		preferDealTypeWithOrders()
		const q = { ...route.query } as Record<string, string>
		if (counterpartyFilterId.value) {
			q.counterparty_id = String(counterpartyFilterId.value)
		} else {
			delete q.counterparty_id
		}
		void router.replace({ query: q })
	},
)

/** deals грузятся async — без этого остаёмся на дефолтных «Закупках» при пустом списке */
watch(isDealsLoaded, (loaded) => {
	if (loaded) preferDealTypeWithOrders()
})

onMounted(() => {
	const raw = route.query.counterparty_id
	const id = Number(Array.isArray(raw) ? raw[0] : raw)
	if (Number.isFinite(id) && id > 0) {
		counterpartyFilterId.value = id
	}
	void loadContracts()
})

const handleSelectCounterparty = (value: number | null) => {
	counterpartyFilterId.value = value
}

const filteredContracts = computed(() => {
	// Договоры ЛК только при выбранном контрагенте — иначе при «Все» они
	// прилипают к любому заказу и ломают счётчик строк.
	if (!counterpartyFilterId.value) return []
	let list = companyContracts.value
	if (typeFilter.value !== "all" && typeFilter.value !== "company_contract") {
		return []
	}
	if (dateFrom.value) {
		list = list.filter((c) => (c.date || "").slice(0, 10) >= dateFrom.value)
	}
	if (dateTo.value) {
		list = list.filter((c) => (c.date || "").slice(0, 10) <= dateTo.value)
	}
	return list
})

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

/** Один заказ или все из текущего фильтра (когда «Все заказы»). */
const dealIdsToLoad = computed((): number[] => {
	if (!isDealsLoaded.value || !orderOptions.value.length) return []
	if (selectedDealId.value == null) {
		return orderOptions.value.map((o) => o.value)
	}
	if (!hasValidSelectedDeal.value) return []
	return [selectedDealId.value]
})

const {
	data: documentsFromApi,
	error: documentsApiError,
	asyncStatus: documentsApiAsyncStatus,
} = useQuery({
	key: () => [
		QueryKeys.GET_DOCUMENTS_BY_DEAL_ID,
		selectedDealId.value ?? "all",
		...dealIdsToLoad.value,
	],
	query: async () => {
		const ids = dealIdsToLoad.value
		if (!ids.length) return []
		const chunks = await Promise.all(
			ids.map((id) => documentsApi.getDocumentsByDealId(id)),
		)
		return chunks.flatMap((list) => list ?? [])
	},
	enabled: () => dealIdsToLoad.value.length > 0,
});

watch(documentsApiError, (err) => {
	if (!err) return;
	toast.add({
		title: "Ошибка",
		description: "Не удалось загрузить список документов",
		color: "error",
	});
});

/** Blob вне Vue-state; качаем лениво при «Скачать», в таблицу кладём только метаданные */
const blobByDocumentId = new Map<number, Blob>()
const generatedDocuments = shallowRef<DocumentApiItem[]>([]);
const isGeneratingDocs = ref(false);

const buildSyntheticDocsForDeal = async (dealId: number): Promise<DocumentApiItem[]> => {
	const orderMeta = orderOptions.value.find((o) => o.value === dealId)
	const orderNumber = orderMeta?.orderNumber?.trim()
	const listDeal =
		dealTypeFilter.value === "purchases"
			? purchaseOrdersForFilter.value.find((d) => d.id === dealId)
			: salesOrdersForFilter.value.find((d) => d.id === dealId)
	const date = listDeal?.created_at || listDeal?.updated_at || ""

	const docs: DocumentApiItem[] = []
	if (orderNumber) {
		docs.push({
			document_id: dealId,
			deal_id: dealId,
			document_type: "order",
			document_number: orderNumber,
			document_date: date,
			document_file_path: null,
			created_at: date,
			updated_at: date,
		})
	}

	await ensureDealLoaded(dealId)
	const deal = findDeal(dealId)
	if (deal && isBillCreatedInDeal(deal)) {
		docs.push({
			document_id: dealId + BILL_SYNTHETIC_ID_OFFSET,
			deal_id: dealId,
			document_type: "bill",
			document_number: deal.bill.number ?? null,
			document_date: deal.billDate || deal.date || date,
			document_file_path: null,
			created_at: deal.date || date,
			updated_at: deal.date || date,
		})
	}
	return docs
}

let syntheticDocsLoadSeq = 0
watch(
	[dealIdsToLoad, dealTypeFilter, isDealsLoaded, orderOptions],
	async () => {
		if (import.meta.server) return
		const seq = ++syntheticDocsLoadSeq
		const ids = [...dealIdsToLoad.value]
		if (!ids.length) {
			if (seq === syntheticDocsLoadSeq) {
				generatedDocuments.value = []
				blobByDocumentId.clear()
			}
			return
		}
		getDeals()
		isGeneratingDocs.value = true
		generatedDocuments.value = []
		try {
			const chunks = await Promise.all(ids.map((id) => buildSyntheticDocsForDeal(id)))
			// Старый запрос «Все заказы» не должен затереть выбранный номер
			if (seq !== syntheticDocsLoadSeq) return
			blobByDocumentId.clear()
			generatedDocuments.value = chunks.flat()
		} finally {
			if (seq === syntheticDocsLoadSeq) {
				isGeneratingDocs.value = false
			}
		}
	},
	{ immediate: true },
);

const documents = computed<DocumentApiItem[]>(() => {
	if (!dealIdsToLoad.value.length) return []
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

const getFileFormat = (path: string | null, documentType?: string): string => {
	if (path) {
		const extension = path.split(".").pop();
		if (extension) return extension.toUpperCase();
	}
	// Сгенерированные заказ/счёт — всегда docx, файла в storage нет
	if (documentType === "order" || documentType === "bill") return "DOCX";
	return "—";
};

const tableRows = computed<DocumentTableRow[]>(() =>
	documents.value.map((item, index) => ({
		index: index + 1,
		id: item.document_id,
		dealId: item.deal_id,
		orderNumber: orderMap.value[item.deal_id] || `#${item.deal_id}`,
		documentNumber: item.document_number || `Документ #${item.document_id}`,
		documentType: getDocumentTypeLabel(item.document_type),
		format: getFileFormat(item.document_file_path, item.document_type),
		rawType: item.document_type,
		rawDate: item.document_date || item.created_at || "",
	})),
);

type UnifiedDocRow = DocumentTableRow & {
	rawType?: string
	rawDate?: string
	kind?: "deal" | "contract"
	contractId?: number
}

const filteredDealRows = computed((): UnifiedDocRow[] => {
	if (typeFilter.value === "company_contract") return []
	let rows = tableRows.value as UnifiedDocRow[]
	if (typeFilter.value !== "all") {
		rows = rows.filter((r) => r.rawType === typeFilter.value)
	}
	if (dateFrom.value) {
		rows = rows.filter((r) => String(r.rawDate || "").slice(0, 10) >= dateFrom.value)
	}
	if (dateTo.value) {
		rows = rows.filter((r) => String(r.rawDate || "").slice(0, 10) <= dateTo.value)
	}
	return rows.map((r) => ({ ...r, kind: "deal" as const }))
})

const contractAsRows = computed((): UnifiedDocRow[] => {
	// Договоры не привязаны к заказу, но если в текущем режиме нет заказов,
	// а в другом есть — не показываем их (иначе кажется, что «в Закупках есть документы»).
	if (!orderOptions.value.length && hasOrdersOnOtherSide.value) {
		return []
	}
	return filteredContracts.value.map((c) => ({
		id: c.id,
		index: 0,
		dealId: 0,
		orderNumber: "—",
		documentNumber: `${c.number} от ${normalizeDate(c.date) || "—"}`,
		documentType: "Договор",
		format: "—",
		rawType: "company_contract",
		rawDate: c.date || "",
		kind: "contract" as const,
		contractId: c.id,
	}))
})

/** Одна таблица: договоры ЛК + документы заказа */
const unifiedTableRows = computed(() =>
	[...contractAsRows.value, ...filteredDealRows.value].map((r, i) => ({
		...r,
		index: i + 1,
	})),
)

watch(
	[orderOptions, isDealsLoaded],
	() => {
		// До загрузки сделок не трогаем выбор — иначе сбрасывается dealId из URL
		if (!isDealsLoaded.value) return
		const options = orderOptions.value
		if (!options.length) {
			selectedDealId.value = null
			return
		}
		if (
			selectedDealId.value != null &&
			!options.some((o) => o.value === selectedDealId.value)
		) {
			selectedDealId.value = null
		}
	},
	{ flush: "post" },
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
}>({
	documentType: null,
	documentNumber: "",
});
/** File отдельно — иначе reactive+File ломает SSR/payload */
const uploadFile = ref<File | null>(null)

const isUploadDisabled = computed(() => {
	if (!selectedDealId.value) return true;
	if (!uploadForm.documentType) return true;
	return !uploadFile.value;
});

const handleSelectDealType = (dealType: DealTypeFilter): void => {
	if (!dealType) return;
	dealTypeFilter.value = dealType;
	const currentOptions = orderOptions.value;
	const stillValid =
		selectedDealId.value != null &&
		currentOptions.some((o) => o.value === selectedDealId.value);
	if (!stillValid) selectedDealId.value = null
};

const handleSelectDeal = (dealId: number | null): void => {
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
	uploadFile.value = null;
	isUploadModalOpen.value = true;
};

const handleOpenFilePicker = (): void => {
	fileInputRef.value?.click();
};

const handleFileChange = (event: Event): void => {
	const target = event.target as HTMLInputElement;
	const selectedFile = target.files?.[0];
	uploadFile.value = selectedFile || null;
};

const handleUploadDocument = async (): Promise<void> => {
	if (!selectedDealId.value || !uploadForm.documentType || !uploadFile.value) return;

	const formData = new FormData();
	formData.append("file", uploadFile.value);
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
	if (!row.dealId) return;

	try {
		const result = await documentsApi.downloadDocument(
			row.dealId,
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

const handleDeleteDocument = (row: DocumentTableRow): void => {
	if (!row.dealId) return;

	const dealId = row.dealId;
	askDelete({
		message: `Точно хотите удалить документ «${row.documentType || row.documentNumber || row.id}»?\nЭто действие нельзя отменить.`,
		onConfirm: async () => {
			try {
				await deleteDocumentAsync(dealId, row.id);
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
				throw error;
			}
		},
	});
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
			const rowData = row.original as UnifiedDocRow;
			if (rowData.kind === "contract") {
				return h(UButton, {
					label: "Открыть",
					size: "xs",
					color: "neutral",
					variant: "soft",
					onClick: () => {
						void router.push({
							path: "/profile/contracts",
							query: rowData.contractId
								? { highlight: String(rowData.contractId) }
								: undefined,
						});
					},
				});
			}
			return h(UDropdownMenu, {
				items: [
					{
						label: "Скачать",
						icon: "i-lucide-download",
						color: "primary",
						variant: "soft",
						onClick: () => {
							void (async () => {
								const synthetic =
									rowData.rawType === "order" || rowData.rawType === "bill"
								if (synthetic) {
									try {
										let blob = blobByDocumentId.get(rowData.id)
										if (!blob) {
											blob = await fetchDealGeneratedDocxBlob(
												rowData.dealId,
												rowData.rawType === "bill" ? "bill" : "order",
											)
											blobByDocumentId.set(rowData.id, blob)
										}
										downloadBlob(blob, `document-${rowData.orderNumber}`)
									} catch (e) {
										if (import.meta.dev) console.error("download synthetic:", e)
										toast.add({
											title: "Ошибка",
											description: "Не удалось скачать документ",
											color: "error",
										})
									}
									return
								}
								await handleDownloadDocument(rowData)
							})()
						},
					},
					{
						label: "Удалить",
						icon: "i-lucide-trash-2",
						color: "error",
						variant: "soft",
						onClick: () =>
							rowData.rawType === "order" || rowData.rawType === "bill"
								? handleDeleteDocumentWithBlob()
								: handleDeleteDocument(rowData),
					},
					{
						label: "Просмотр",
						icon: "i-lucide-eye",
						onClick: () => {
							// Сгенерированные заказ/счёт открываем в редакторе
							if (rowData.rawType === "order" || rowData.rawType === "bill") {
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
	[() => route.query.dealId, isDealsLoaded, orderOptions],
	() => {
		if (!isDealsLoaded.value || !orderOptions.value.length) return
		const raw = route.query.dealId
		if (raw == null || raw === "") return
		const parsedDealId = Number(Array.isArray(raw) ? raw[0] : raw)
		if (!Number.isFinite(parsedDealId) || parsedDealId <= 0) return
		if (!orderOptions.value.some((o) => o.value === parsedDealId)) return
		if (selectedDealId.value !== parsedDealId) {
			selectedDealId.value = parsedDealId
		}
	},
	{ immediate: true },
);

watch(
	() => selectedDealId.value,
	() => {
		if (!isDealsLoaded.value || !orderOptions.value.length) return
		const q = { ...route.query } as Record<string, string>
		if (selectedDealId.value != null && hasValidSelectedDeal.value) {
			q.dealId = String(selectedDealId.value)
		} else if (selectedDealId.value == null) {
			delete q.dealId
		}
		const cur = route.query.dealId
		const next = q.dealId
		if (String(cur ?? "") === String(next ?? "")) return
		void router.replace({ query: q })
	},
);
</script>
