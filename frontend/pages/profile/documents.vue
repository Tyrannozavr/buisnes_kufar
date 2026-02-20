<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg p-4 space-y-4">

      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div class="flex flex-wrap gap-3 md:flex-row md:items-end">
          <div class="w-full md:w-48">
            <UFormField label="Закупки / Продажи">
              <USelect :model-value="dealTypeFilter" :items="DEAL_TYPE_OPTIONS" value-key="value" label-key="label"
                placeholder="Выберите" @update:model-value="handleSelectDealType" />
            </UFormField>
          </div>
          <div class="w-full md:max-w-md">
            <UFormField label="Номер заказа">
              <USelect :model-value="selectedDealId" :items="orderOptions" value-key="value" label-key="label"
                placeholder="Выберите заказ" @update:model-value="handleSelectDeal" />
            </UFormField>
          </div>
        </div>

        <UButton color="primary" icon="i-lucide-upload" :disabled="!selectedDealId" @click="handleOpenUploadModal">
          Загрузить документ
        </UButton>
      </div>

      <UTable sticky :data="tableRows" :columns="columns" class="max-h-100 overflow-y-auto overscroll-auto" />
    </div>

    <UModal v-model:open="isUploadModalOpen" title="Загрузка документа">
      <template #body>
        <div class="space-y-4 p-4">
          <UFormField label="Тип документа">
            <USelect class="w-1/2" :model-value="uploadForm.documentType" :items="DOCUMENT_TYPE_OPTIONS"
              label-key="label" value-key="value" placeholder="Выберите тип документа"
              @update:model-value="handleSelectDocumentType" />
          </UFormField>

          <UFormField label="Номер документа (необязательно)">
            <UInput class="w-1/2" v-model="uploadForm.documentNumber" placeholder="Например, INV-001" />
          </UFormField>

          <UFormField label="Файл">
            <div class="flex items-center gap-3">
              <UButton class="w-1/2" color="neutral" variant="outline" icon="i-lucide-file-up"
                @click="handleOpenFilePicker">
                Выбрать документ/скан
              </UButton>
              <span class="text-sm text-gray-600 truncate">
                {{ uploadForm.file?.name || "Файл не выбран" }}
              </span>
            </div>
            <input ref="fileInputRef" class="hidden" type="file" aria-label="Выберите файл документа"
              @change="handleFileChange" />
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
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { useDocumentsApi } from "~/api/documents";
import { usePurchasesApi } from "~/api/purchases";
import {
  DEAL_TYPE_OPTIONS,
  DOCUMENT_TYPE_LABELS,
  DOCUMENT_TYPE_OPTIONS,
  type DealTypeFilter,
  type DocumentApiItem,
  type DocumentTableRow,
  type DocumentTypeCode,
  type OrderOption,
} from "~/types/documents";
import type { BuyerDealResponse, SellerDealResponse } from "~/types/dealReasponse";
import { usePurchasesStore } from "~/stores/purchases";
import { useSalesStore } from "~/stores/sales";
import { useDocxGenerator } from "~/composables/useDocxGenerator";
import { useRoute, useRouter } from "vue-router";

definePageMeta({
  layout: "profile",
});

const toast = useToast();
const route = useRoute();
const router = useRouter();
const documentsApi = useDocumentsApi();
const purchasesApi = usePurchasesApi();
const UButton = resolveComponent("UButton");
const USelect = resolveComponent("USelect");
const purchasesStore = usePurchasesStore();
const salesStore = useSalesStore();
const { generateDocxOrder, generateDocxBill, downloadBlob } = useDocxGenerator();

const dealTypeFilter = ref<DealTypeFilter>("purchases");
const selectedDealId = ref<number | null>(null);
const orderMap = ref<Record<number, string>>({});
const buyerDeals = ref<(BuyerDealResponse | SellerDealResponse)[]>([]);
const sellerDeals = ref<(BuyerDealResponse | SellerDealResponse)[]>([]);
const documents = ref<DocumentApiItem[]>([]);
const isLoadingDocuments = ref(false);

const isUploadModalOpen = ref(false);
const isUploading = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const uploadForm = reactive<{
  documentType: DocumentTypeCode | null;
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

const orderOptions = computed<OrderOption[]>(() => {
  const deals =
    dealTypeFilter.value === "purchases" ? buyerDeals.value : sellerDeals.value;

  return deals.map((deal) => ({
    value: deal.id,
    orderNumber: deal.buyer_order_number,
    label: `№ ${deal.buyer_order_number}`,
  }));
});

const handleSelectDealType = (dealType: DealTypeFilter): void => {
  if (!dealType) return;
  dealTypeFilter.value = dealType
  const currentOptions = orderOptions.value;

  const stillValid =
    selectedDealId.value &&
    currentOptions.some((o) => o.value === selectedDealId.value);

  if (!stillValid) {
    selectedDealId.value = currentOptions[0]?.value ?? null;
  }
};

const handleSelectDeal = (dealId: number): void => {
  console.log('dealId: ', dealId);
  selectedDealId.value = dealId;
};

const handleSelectDocumentType = (documentType: DocumentTypeCode): void => {
  console.log('documentType: ', documentType);
  uploadForm.documentType = documentType;
};

const getDocumentTypeLabel = (documentType: string): string => {
  return DOCUMENT_TYPE_LABELS[documentType] || documentType;
};

const getFileFormat = (path: string | null): string => {
  if (!path) return "-";
  const extension = path.split(".").pop();
  if (!extension) return "-";
  return extension.toUpperCase();
};

//загрузка сделок, заполнение orderMap, выбор дефолтной сделки
const loadDeals = async (): Promise<void> => {
  const [buyer, seller] = await Promise.all([
    purchasesApi.getBuyerDeals(),
    purchasesApi.getSellerDeals(),
  ]);

  const buyerList = (buyer || []).sort((a, b) => b.id - a.id);
  const sellerList = (seller || []).sort((a, b) => b.id - a.id);

  buyerDeals.value = buyerList;
  sellerDeals.value = sellerList;

  //объект в котором id сделки соответствует номеру заказа
  const map: Record<number, string> = {};

  buyerList.forEach((deal) => {
    map[deal.id] = deal.buyer_order_number;
  });

  sellerList.forEach((deal) => {
    map[deal.id] = deal.seller_order_number;
  });

  orderMap.value = map;

  //дефолтное значение сделки покупателя или продавца
  const options =
    dealTypeFilter.value === "purchases"
      ? buyerList
      : sellerList

  const firstId = options[0]?.id ?? null;
  if (!selectedDealId.value || !options.some((d) => d.id === selectedDealId.value)) {
    selectedDealId.value = firstId;
  }
};

//функция, получающая данные сделки по selectedDealId из store и преобразующая их в массив объектов DocumentApiItem + генерация Blob для создания документа из таблицы
const createDocumentsFromState = async (dealId: number): Promise<DocumentApiItem[]> => {
  if (dealTypeFilter.value === "purchases") {
    await purchasesStore.getDeals();
  } else if (dealTypeFilter.value === "sales") {
    await salesStore.getDeals();
  } else {
    return [];
  }

  const store = dealTypeFilter.value === "purchases" ? purchasesStore : salesStore;

  const deal = store.findGoodsDeal(dealId) ?? store.findServicesDeal(dealId);
  if (!deal) return [];

  console.log('deal: ', deal);
  const orderNumber = dealTypeFilter.value === "purchases" ? deal.buyerOrderNumber : deal.sellerOrderNumber;

  const docs = []
  if (orderNumber) {
    const blob = await generateDocxOrder(deal);
    docs.push({
      document_id: deal.dealId,
      deal_id: deal.dealId,
      document_type: "order",
      document_number: orderNumber ?? null,
      document_date: deal.date,
      document_file_path: null,
      created_at: deal.date,
      updated_at: deal.date,
      blob: blob,
    });
  }
  if (deal.billNumber) {
    const blob = await generateDocxBill(deal);
    docs.push({
      document_id: deal.dealId + 1_000_000,
      deal_id: deal.dealId,
      document_type: "bill",
      document_number: deal.billNumber ?? null,
      document_date: deal.billDate ?? null,
      document_file_path: null,
      created_at: deal.billDate ?? deal.date,
      updated_at: deal.billDate ?? deal.date,
      blob: blob,
    });
  }
  console.log("docs", docs)
  return docs;
};

//загрузка документов по selectedDealId
const loadDocuments = async (): Promise<void> => {
  if (!selectedDealId.value) {
    documents.value = [];
    return;
  }

  isLoadingDocuments.value = true;
  try {

    const dataFromDeal = await createDocumentsFromState(selectedDealId.value);
    const dataFromApi = await documentsApi.getDocumentsByDealId(selectedDealId.value);
    const data = [...dataFromDeal, ...(dataFromApi || [])];

    documents.value = data;

  } catch (error) {
    documents.value = [];
    console.log("ERROR: ", error);

    toast.add({
      title: "Ошибка",
      description: "Не удалось загрузить список документов",
      color: "error",
    });

  } finally {
    isLoadingDocuments.value = false;
  }
};

//очищение формы перед открытием модального окна
const handleOpenUploadModal = (): void => {
  uploadForm.documentType = DOCUMENT_TYPE_OPTIONS[0]?.value || null;
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

  isUploading.value = true;
  try {
    await documentsApi.uploadDocumentById(selectedDealId.value, formData);

    toast.add({
      title: "Успешно",
      description: "Документ загружен",
      color: "success",
    });

    isUploadModalOpen.value = false;

    await loadDocuments();
  } catch (error) {
    toast.add({
      title: "Ошибка",
      description: "Не удалось загрузить документ",
      color: "error",
    });
    console.log("ERROR: ", error);
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
      const baseName = `document-${row.orderNumber}`;
      a.download = baseName;
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
    console.error("ERROR: ", error);
  }
};

const handleDeleteDocument = async (row: DocumentTableRow): Promise<void> => {
  if (!selectedDealId.value) return;

  try {
    await documentsApi.deleteDocument(selectedDealId.value, row.id);
    toast.add({
      title: "Успешно",
      description: "Документ удален",
      color: "success",
    });
    await loadDocuments();
  } catch (error) {
    toast.add({
      title: "Ошибка",
      description: "Не удалось удалить документ",
      color: "error",
    });
    console.log("ERROR: ", error);
  }
};

const handleDeleteDocumetWithBlob = (row: DocumentTableRow): void => {
  //FIXME: если есть blob, то удаляем все поля в store, связанные с этим документом 
  //сейчас временно просто показываем toast
  toast.add({
    title: "Ой!",
    description: "Удаление документов, созданных из таблицы пока не реализовано",
    color: "info",
  });
}

const tableRows = computed<DocumentTableRow[]>(() => {
  return documents.value.map((item, index) => ({
    index: index + 1,
    id: item.document_id,
    dealId: item.deal_id,
    orderNumber: orderMap.value[item.deal_id] || `#${item.deal_id}`,
    documentNumber: item.document_number || `Документ #${item.document_id}`,
    documentType: getDocumentTypeLabel(item.document_type),
    format: getFileFormat(item.document_file_path),
    blob: item.blob,
  }));
});

const columns: TableColumn<DocumentTableRow>[] = [
  { accessorKey: "index", header: "п/п" },
  { accessorKey: "orderNumber", header: "№ заказа" },
  { accessorKey: "documentNumber", header: "№ документа" },
  { accessorKey: "documentType", header: "Тип документа" },
  { accessorKey: "format", header: "Формат" },
  {
    id: "actions",
    header: "Действия",
    cell: ({ row }) => {
      const rowData = row.original;
      return h("div", { class: "flex items-center gap-2" }, [
        h(UButton, {
          size: "xs",
          color: "primary",
          variant: "soft",
          icon: "i-lucide-download",
          label: "Скачать",
          onClick: () => rowData.blob ? downloadBlob(rowData.blob, `document-${rowData.orderNumber}`) : handleDownloadDocument(rowData),
        }),
        h(UButton, {
          size: "xs",
          color: "error",
          variant: "soft",
          icon: "i-lucide-trash-2",
          label: "Удалить",
          onClick: () => rowData.blob ? handleDeleteDocumetWithBlob(rowData) : handleDeleteDocument(rowData),
        }),

      ]);
    },
  },
];

watch(() => route.query,
  () => {
    if (route.query.dealId) {
      selectedDealId.value = Number(route.query.dealId);
    }
}, { immediate: true })

watch(
  () => selectedDealId.value,
  async () => {
    if (selectedDealId.value) {
      await loadDocuments();
      router.replace({ query: {...route.query, dealId: selectedDealId.value.toString()}})
    }
  },
);

onMounted(async () => {
  await loadDeals();
  await loadDocuments();
});
</script>
