<template>
	<div class="px-4 pb-4">
		<div v-if="isTableLoading" class="flex justify-center py-12">
			<UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-400" />
		</div>
		<template v-else>
		<UTable
			v-model:sorting="tableSorting"
			v-model:pagination="tablePagination"
			:pagination-options="paginationOptions"
			:data="type === 'purchases' ? purchasesTable : salesTable"
			:columns="activeTableColumns"
		/>

		<div v-if="tableRowCount > PAGE_SIZE" class="mt-4 flex justify-center">
			<UPagination
				v-model="currentPage"
				:total="tableRowCount"
				:per-page="PAGE_SIZE"
			/>
		</div>
		</template>
	</div>

	<UModal v-model:open="isSupplyContractChoiceModalOpen" title="Договор поставки уже существует">
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">
					Для сделки № {{ selectedSupplyContractDealNumber }} найден действующий договор поставки с данным покупателем. Вы можете создать спецификацию к существующему договору или создать новый договор поставки.
				</p>
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton
						label="Создать спецификацию"
						color="primary"
						class="w-full justify-center"
						:loading="isSupplyContractActionBusy"
						:disabled="isSupplyContractActionBusy"
						@click="handleOpenSupplyContractSelection"
					/>
					<UButton
						label="Создать новый договор"
						color="neutral"
						variant="subtle"
						class="w-full justify-center"
						:loading="isSupplyContractActionBusy"
						:disabled="isSupplyContractActionBusy"
						@click="handleCreateNewSupplyContractFromChoice"
					/>
				</div>
			</div>
		</template>
	</UModal>

	<UModal v-model:open="isSupplyContractSelectionModalOpen" title="Выбор договора поставки">
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">
					Выберите договор с данным покупателем, по которому нужно создать новую спецификацию.
				</p>
				<USelect
					:disabled="isSupplyContractActionBusy"
					:items="supplyContractSelectionItems"
					:model-value="selectedSupplyContractEntityId"
					placeholder="Выберите договор"
					@update:model-value="handleSupplyContractSelectionChange"
				/>
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton
						label="Выбор"
						color="primary"
						class="w-full justify-center"
						:loading="isSupplyContractActionBusy"
						:disabled="isSupplyContractActionBusy || !selectedSupplyContractEntityId"
						@click="handleCreateSpecificationForSelectedContract"
					/>
					<UButton
						label="Отмена"
						color="neutral"
						variant="subtle"
						class="w-full justify-center"
						:disabled="isSupplyContractActionBusy"
						@click="handleCancelSupplyContractSelection"
					/>
				</div>
			</div>
		</template>
	</UModal>

	<CreateBillFromSalesDialogs />

	<UModal v-model:open="isSupplyDocTypeModalOpen" title="Выберите тип документа">
		<template #body>
			<div class="flex flex-col gap-3">
				<URadioGroup v-model="supplyDocTypeRadio" :items="supplyDocTypeItems" />
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton label="Создать" color="primary" class="w-full justify-center" :loading="isSupplyContractActionBusy" @click="handleSupplyDocTypeConfirm" />
					<UButton label="Отмена" color="neutral" variant="subtle" class="w-full justify-center" @click="isSupplyDocTypeModalOpen = false" />
				</div>
			</div>
		</template>
	</UModal>

	<UModal v-model:open="isTransportContractModalOpen" title="Договор транспортной экспедиции">
		<template #body>
			<div class="flex flex-col gap-3">
				<p class="text-sm text-gray-600">Выберите существующий договор или создайте новый (MVP).</p>
				<USelect
					v-if="transportContractSelectionItems.length"
					:items="transportContractSelectionItems"
					:model-value="selectedTransportContractValue"
					placeholder="Выберите договор"
					@update:model-value="handleTransportSelectionChange"
				/>
				<div class="flex flex-col gap-2 sm:flex-row">
					<UButton label="Выбор" color="primary" class="w-full justify-center" :loading="isTransportActionBusy" :disabled="!selectedTransportContractValue" @click="handleBindTransportContract" />
					<UButton label="Создать новый" color="neutral" variant="subtle" class="w-full justify-center" :loading="isTransportActionBusy" @click="handleCreateNewTransportContract" />
					<UButton label="Отмена" color="neutral" variant="ghost" class="w-full justify-center" @click="isTransportContractModalOpen = false" />
				</div>
			</div>
		</template>
	</UModal>
</template>

<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { getPaginationRowModel } from "@tanstack/vue-table";
import { normalizeDate, normalizeSpecificationNumber, formatDocumentLinkLabel } from "~/utils/normalize";
import { renderTz15DocCell } from "~/utils/tz15DocumentCell";
import { useRouter } from "vue-router";
import { useDeals } from "~/composables/useDeals";
import { useSupplyContractEntity } from "~/composables/useSupplyContractEntity";
import type { Deal } from "~/types/dealState";
import type { BuyerTableItems, SellerTableItems } from "~/types/purchases";
import { usePurchasesApi } from "~/api/purchases";
import { Editor } from "~/constants/keys";
import { useBillFillState } from "~/composables/useBillFillState";
import { useCreateBillFromSales } from "~/composables/useCreateBillFromSales";
import CreateBillFromSalesDialogs from "~/components/EditorMenu/CreateBillFromSalesDialogs.vue";
import type { SpecificationEntityResponse } from "~/types/supplyContractEntity";

const { type, dealFilter = 'Товары' } = defineProps<{
  type: 'purchases' | 'sales'
  dealFilter?: 'Товары' | 'Услуги'
}>()

const router = useRouter()
const UButton = resolveComponent('UButton')
const purchasesApi = usePurchasesApi()
const toast = useToast()
const supplyContractType = useTypedState(Editor.SUPPLY_CONTRACT_TYPE, () => ref<'supplyContract' | 'specification'>('supplyContract'))

const selectedSupplyContractDealId = ref<number | null>(null)
const selectedSupplyContractDealNumber = ref<string>('')
const isContractCheckBusy = ref(false)
const isSupplyContractActionBusy = ref(false)
const isSupplyContractChoiceModalOpen = ref(false)
const isSupplyContractSelectionModalOpen = ref(false)
const isSupplyDocTypeModalOpen = ref(false)
const supplyDocTypeRadio = ref<'supplyContract' | 'specification'>('supplyContract')
const supplyDocTypeItems = [
	{ label: 'Договор поставки товара', value: 'supplyContract' },
	{ label: 'Спецификация к договору поставки', value: 'specification' },
]
const isTransportContractModalOpen = ref(false)
const isTransportActionBusy = ref(false)
const selectedTransportDealNumber = ref('')
const selectedTransportContractValue = ref<string | undefined>()
const transportContractSelectionItems = ref<{ label: string; value: string }[]>([
	{ label: 'Договор экспедиции № TE-001 от 01.01.26', value: 'TE-001' },
])
const selectedSupplyContractEntityId = ref<number | undefined>(undefined)
const {
	contractEntity: checkedSupplyContractEntity,
	refreshStatus: refreshSupplyContractStatus,
	ensureContractEntity,
} = useSupplyContractEntity(selectedSupplyContractDealId)

const { deals, findDealByDealNumber, findDeal, getDeals, isBuyerDealsLoading, isSellerDealsLoading } = useDeals({
	role: type === 'purchases' ? 'buyer' : 'seller',
})
getDeals()
const { clearBillAwaitingFill } = useBillFillState()
const {
	startCreateBill,
} = useCreateBillFromSales()
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const activeTab = useTypedState(Editor.ACTIVE_TAB, () => ref('0'))
const PAGE_SIZE = 10
const tableSorting = ref<{ id: string; desc: boolean }[]>([{ id: 'date', desc: true }])
const tablePagination = ref({ pageIndex: 0, pageSize: PAGE_SIZE })
const paginationOptions = { getPaginationRowModel: getPaginationRowModel() }

const currentPage = computed({
	get: () => tablePagination.value.pageIndex + 1,
	set: (page: number) => {
		tablePagination.value = {
			...tablePagination.value,
			pageIndex: Math.max(0, page - 1),
		}
	},
})

const sortDealsNewestFirst = (deals: Deal[]) =>
	[...deals].sort((a, b) => {
		const byDate = (b.date || '').localeCompare(a.date || '')
		if (byDate !== 0) return byDate
		return (b.dealId ?? 0) - (a.dealId ?? 0)
	})

const dealsList = computed(() => {
	const list = deals.value ?? []
	return type === 'purchases'
		? list.filter(deal => deal.role === 'buyer')
		: list.filter(deal => deal.role === 'seller')
})

/** Закладка «Товары» / «Услуги» — фильтр по типу сделки (§2.3, §4.6). */
const goodsDealsList = computed(() =>
	dealsList.value.filter(deal => deal.dealType === dealFilter),
)
const purchasesTable: Ref<BuyerTableItems[]> = ref([])
const salesTable: Ref<SellerTableItems[]> = ref([])

const tableRowCount = computed(() =>
	type === 'purchases' ? purchasesTable.value.length : salesTable.value.length,
)

const isTableLoading = computed(() => {
	if (!import.meta.client) return true
	return type === 'purchases' ? isBuyerDealsLoading.value : isSellerDealsLoading.value
})


const getDealIdByDealNumber = (dealNumber: string, role: 'buyer' | 'seller'): number | undefined => {
  return findDealByDealNumber(dealNumber, role)?.dealId
}

const openEditor = (dealId: number | undefined, role: 'buyer' | 'seller', hash: string) => {
	if (!dealId) return
	router.push({
		path: '/profile/editor',
		query: { dealId: String(dealId), role },
		hash,
	})
}

const hasBill = (deal?: Deal) => Boolean(deal?.billDate || deal?.bill?.number)
const hasSupplyContract = (deal?: Deal) => Boolean(deal?.supplyContractDate)
const hasSpecification = (deal?: Deal) => Boolean(
	deal?.supplyContract.specificationEntityId || deal?.supplyContract.specificationNumber,
)

const formatBillDocLabel = (deal: Deal): string | null => {
	if (!hasBill(deal)) return null
	return formatDocumentLinkLabel(deal.bill.number, deal.billDate)
}

const formatTransportDocLabel = (deal: Deal): string | null => {
	const tc = deal.transportContract
	if (!tc?.number) return null
	const dateStr = tc.date ? normalizeDate(String(tc.date).slice(0, 10)) : ''
	return formatDocumentLinkLabel(tc.number, dateStr)
}

const formatClosingDocLabel = (deal: Deal): string | null => {
	const docs = (deal.closingDocuments ?? []) as { name?: string; number?: string; date?: string; type?: string }[]
	if (!docs.length) return null
	const first = docs[docs.length - 1]
	if (first?.name) return first.name
	if (first?.number) {
		const typeLabel = first.type === 'UPD' ? 'УПД' : (first.type || 'Документ')
		return `${typeLabel} № ${first.number}${first.date ? ` от ${normalizeDate(String(first.date).slice(0, 10))} г.` : ''}`
	}
	return null
}

const formatBillCellLabel = (deal: Deal): string => {
	if (!hasBill(deal)) {
		return type === 'sales' ? 'Создать счет' : 'Просмотр'
	}
	return formatDocumentLinkLabel(deal.bill.number, deal.billDate)
}

const formatContractCellLabel = (deal: Deal): string => {
	const items = (deal.contract ?? []) as { number?: string; date?: string }[]
	const first = items[0]
	const number = first?.number ?? ''
	const date = first?.date ?? deal.contractDate ?? ''
	return formatDocumentLinkLabel(number, date)
}

const formatAccompanyingCellLabel = (deal: Deal): string => {
	const names = (deal.closingDocuments ?? [])
		.map((document: { name?: string }) => document?.name)
		.filter(Boolean)
	if (names.length) return names.join(', ')
	return type === 'sales' ? 'Создать документ' : 'Просмотр'
}

const formatInvoiceCellLabel = (_deal: Deal): string =>
	type === 'sales' ? 'Создать счет-фактуру' : 'Просмотр'

const formatActCellLabel = (_deal: Deal): string =>
	type === 'sales' ? 'Создать акт' : 'Просмотр'

const formatOthersCellLabel = (deal: Deal): string => {
	const names = (deal.othersDocuments ?? [])
		.map((document: { name?: string }) => document?.name)
		.filter(Boolean)
	if (names.length) return names.join(', ')
	return 'Просмотр'
}

const editorHashForDocument = (
	documentType: 'order' | 'bill' | 'supplyContract' | 'accompanyingDocuments' | 'invoice' | 'othersDocument' | 'contract' | 'act',
): string => {
	const map = {
		order: '#order',
		bill: '#bill',
		supplyContract: '#supplyContract',
		accompanyingDocuments: '#accompanyingDocuments',
		invoice: '#invoice',
		othersDocument: '#othersDocument',
		contract: '#contract',
		act: '#act',
	} as const
	return map[documentType]
}

const getSupplyContractEmptyLabel = () => type === 'sales' ? 'Создать договор поставки' : 'Просмотр'

const formatSupplyContractLabel = (deal: Deal): string => {
	if (!hasSupplyContract(deal)) {
		return getSupplyContractEmptyLabel()
	}

	const contractNumber = deal.supplyContract.number || deal.sellerOrderNumber || ''
	const contractDate = deal.supplyContract.entityDate || deal.supplyContractDate || ''
	const contractLine = formatDocumentLinkLabel(contractNumber, contractDate)

	if (!hasSpecification(deal)) {
		return contractLine
	}

	const specNumber = normalizeSpecificationNumber(deal.supplyContract.specificationNumber)
	if (!specNumber) {
		return contractLine
	}

	return `${contractLine}\nСпецификация №${specNumber}`
}

const TABLE_LINK_CLASS = 'text-sky-500 text-wrap cursor-pointer'

const renderSupplyContractButton = (label: string, onClick: () => void) => h(
	UButton,
	{
		color: 'neutral',
		variant: 'ghost',
		class: `${TABLE_LINK_CLASS} h-auto`,
		ui: { base: 'items-start cursor-pointer' },
		onClick,
	},
	() => h('span', { class: 'whitespace-pre-line text-left leading-snug cursor-pointer' }, label),
)

type SupplyContractSelectionOption = {
	id: number
	number: string
	date: string
	termsText: string
	supplierDetailsCheck: boolean
	buyerDetailsCheck: boolean
	coverLetterCheck: boolean
}

const supplyContractSelectionOptions = computed<SupplyContractSelectionOption[]>(() => {
	const dealId = selectedSupplyContractDealId.value
	if (!dealId) {
		return []
	}

	const selectedDeal = findDeal(dealId)
	if (!selectedDeal?.buyer?.companyId || !selectedDeal?.seller?.companyId) {
		return []
	}

	const byId = new Map<number, SupplyContractSelectionOption>()
	const buyerCompanyId = selectedDeal.buyer.companyId
	const sellerCompanyId = selectedDeal.seller.companyId

	for (const deal of deals.value ?? []) {
		if (deal.role !== 'seller') continue
		if (deal.buyer.companyId !== buyerCompanyId) continue
		if (deal.seller.companyId !== sellerCompanyId) continue

		const contractId = Number(deal.supplyContract.entityId)
		if (!Number.isFinite(contractId) || contractId <= 0) continue

		if (!byId.has(contractId)) {
			byId.set(contractId, {
				id: contractId,
				number: deal.supplyContract.number || deal.sellerOrderNumber || '',
				date: deal.supplyContract.entityDate || deal.supplyContractDate || deal.date,
				termsText: deal.supplyContract.supplyContractText ?? '',
				supplierDetailsCheck: Boolean(deal.supplyContract.supplierDetailsCheck),
				buyerDetailsCheck: Boolean(deal.supplyContract.buyerDetailsCheck),
				coverLetterCheck: Boolean(deal.supplyContract.coverLetterCheck),
			})
		}
	}

	const checkedContract = checkedSupplyContractEntity.value
	if (checkedContract?.id && !byId.has(checkedContract.id)) {
		byId.set(checkedContract.id, {
			id: checkedContract.id,
			number: checkedContract.number ?? '',
			date: checkedContract.date ?? '',
			termsText: checkedContract.terms_text ?? '',
			supplierDetailsCheck: Boolean(checkedContract.supplier_details_check),
			buyerDetailsCheck: Boolean(checkedContract.buyer_details_check),
			coverLetterCheck: Boolean(checkedContract.cover_letter_check),
		})
	}

	return Array.from(byId.values()).sort((a, b) => (b.date || '').localeCompare(a.date || ''))
})

const supplyContractSelectionItems = computed(() =>
	supplyContractSelectionOptions.value.map((contract) => ({
		label: `№ ${contract.number} от ${normalizeDate(contract.date)}`,
		value: contract.id,
	})),
)

watch(goodsDealsList, () => {
	tablePagination.value = { pageIndex: 0, pageSize: PAGE_SIZE }
  purchasesTable.value = sortDealsNewestFirst(goodsDealsList.value).map(deal => ({
    dealNumber: deal.buyerOrderNumber || '',
    date: deal.date,
    sellerCompany: deal.seller.companyName || '',
    status: deal.status,
    bill: formatBillDocLabel(deal),
    supplyContract: formatSupplyContractLabel(deal),
    transportContract: formatTransportDocLabel(deal),
    closingDocuments: formatClosingDocLabel(deal),
    contract: formatContractCellLabel(deal),
    act: formatActCellLabel(deal),
    accompanyingDocuments: formatAccompanyingCellLabel(deal),
    invoice: formatInvoiceCellLabel(deal),
    othersDocument: formatOthersCellLabel(deal),
  }))
}, { immediate: true, deep: true })

const columnsPurchasesGoodsDeals: TableColumn<any>[] = [
  {
    accessorKey: 'dealNumber',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Заказ`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => {
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `№ ${row.getValue('dealNumber')}`,
          class: TABLE_LINK_CLASS,
          onClick: () => {
            if (dealId != null) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer' },
                hash: '#order'
              })
            }
          }
        })
    }
  },
  {
    accessorKey: 'date',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Дата`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => normalizeDate(row.getValue('date'))
  },
  {
    accessorKey: 'sellerCompany',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Поставщик`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => row.getValue('sellerCompany')
  },
  {
    accessorKey: 'status',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Состояние`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => {
      const status = row.getValue('status') as string
      const color = {
        Активная: 'text-emerald-600',
        Завершенная: 'text-gray-500'
      }
      return h('span',
        {
          class: `font-semibold ${color[status as keyof typeof color]}`
        },
        status
      )
    }
  },
  {
    accessorKey: 'bill',
    header: 'Счет',
    cell: ({ row }) => {
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
      const deal = dealId ? findDeal(dealId) : undefined
      const label = row.getValue('bill') as string | null
      return renderTz15Cell(
        label,
        () => {
          if (hasBill(deal)) {
            clearBillAwaitingFill(dealId)
            openEditor(dealId, 'buyer', '#bill')
          } else {
            toast.add({ title: 'Счет пока не создан', color: 'warning', icon: 'i-lucide-file-x' })
          }
        },
        () => {},
        undefined,
      )
    }
  },
  {
    accessorKey: 'supplyContract',
    header: 'Договор поставки',
    cell: ({ row }) => {
			const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
			const deal = dealId ? findDeal(dealId) : undefined
			const label = row.getValue('supplyContract') as string
      return renderSupplyContractButton(label, () => {
				if (hasSupplyContract(deal)) {
					openEditor(dealId, 'buyer', '#supplyContract')
				} else {
					toast.add({ title: 'Договор поставки пока не создан', color: 'warning', icon: 'i-lucide-file-x' })
				}
			})
    }
  },
  {
    accessorKey: 'transportContract',
    header: 'Договор перевозки',
    cell: ({ row }) => {
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
      const label = row.getValue('transportContract') as string | null
      return renderTz15Cell(
        label,
        () => openEditor(dealId, 'buyer', '#contract'),
        () => {},
        [{ label: 'Найти транспорт', onClick: () => router.push('/transport-search') }],
      )
    }
  },
  {
    accessorKey: 'closingDocuments',
    header: 'Закрывающие документы',
    cell: ({ row }) => {
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
      const label = row.getValue('closingDocuments') as string | null
      return renderTz15Cell(
        label,
        () => openEditor(dealId, 'buyer', '#accompanyingDocuments'),
        () => {},
      )
    }
  },
]
////////////////////////////////////////////////////////////

const pickColumnsByAccessor = (
	columns: TableColumn<any>[],
	keys: string[],
): TableColumn<any>[] => {
	const byKey = new Map(
		columns
			.map((column) => {
				const key = (column as { accessorKey?: string }).accessorKey
				return key ? ([key, column] as const) : null
			})
			.filter((entry): entry is readonly [string, TableColumn<any>] => Boolean(entry)),
	)
	return keys.flatMap((key) => {
		const column = byKey.get(key)
		return column ? [column] : []
	})
}

const purchasesContractColumn: TableColumn<any> = {
	accessorKey: 'contract',
	header: 'Договор',
	cell: ({ row }) => {
		const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
		const deal = dealId ? findDeal(dealId) : undefined
		const label = String(row.getValue('contract') ?? '')
		if (!label) {
			return h('span', { class: 'text-neutral-400' }, '—')
		}
		return h(UButton, {
			color: 'neutral',
			variant: 'ghost',
			label,
			class: TABLE_LINK_CLASS,
			onClick: () => {
				if (deal?.contractDate || label !== '—') {
					openEditor(dealId, 'buyer', '#contract')
				}
			},
		})
	},
}

const purchasesActColumn: TableColumn<any> = {
	accessorKey: 'act',
	header: 'Акт',
	cell: ({ row }) => {
		const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
		return h(UButton, {
			color: 'neutral',
			variant: 'ghost',
			label: row.getValue('act'),
			class: TABLE_LINK_CLASS,
			onClick: () => openEditor(dealId, 'buyer', '#act'),
		})
	},
}

const purchasesInvoiceColumnLegacy: TableColumn<any> = {
	accessorKey: 'invoice',
	header: 'Счет-фактура',
	cell: ({ row }) => {
		const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
		return h(UButton, {
			color: 'neutral',
			variant: 'ghost',
			label: row.getValue('invoice'),
			class: TABLE_LINK_CLASS,
			onClick: () => openEditor(dealId, 'buyer', '#invoice'),
		})
	},
}

const purchasesOthersColumnLegacy: TableColumn<any> = {
	accessorKey: 'othersDocument',
	header: 'Другие документы',
	cell: ({ row }) => {
		const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
		return h(UButton, {
			color: 'neutral',
			variant: 'ghost',
			label: row.getValue('othersDocument'),
			class: TABLE_LINK_CLASS,
			onClick: () => openEditor(dealId, 'buyer', '#othersDocument'),
		})
	},
}

const columnsPurchasesServicesDeals: TableColumn<any>[] = [
	...pickColumnsByAccessor(columnsPurchasesGoodsDeals, [
		'dealNumber',
		'date',
		'sellerCompany',
		'status',
		'bill',
	]),
	purchasesContractColumn,
	purchasesActColumn,
	purchasesInvoiceColumnLegacy,
	purchasesOthersColumnLegacy,
]

//sales
const editSalesDocument = async (
	documentType: 'order' | 'bill' | 'supplyContract' | 'accompanyingDocuments' | 'invoice' | 'othersDocument' | 'contract' | 'act',
	dealNumber: string,
) => {
	const dealId = getDealIdByDealNumber(dealNumber, 'seller')

	if (!dealId) return

	const hash = editorHashForDocument(documentType)

	if (documentType === 'bill') {
		await startCreateBill(dealNumber)
		return
	}

	if (documentType === 'order') {
		await router.push({
			path: '/profile/editor',
			query: { dealId: dealId.toString(), role: 'seller' },
			hash,
		})
		return
	}

	if (documentType === 'supplyContract') {
		selectedSupplyContractDealId.value = dealId
		const created = await ensureContractEntity()
		if (!created) {
			return
		}

		activeTab.value = '2'
		await router.push({
			path: '/profile/editor',
			query: { dealId: dealId.toString(), role: 'seller' },
			hash,
		})
		loadDealTrigger.value++
		return
	}

	await router.push({
		path: '/profile/editor',
		query: { dealId: dealId.toString(), role: 'seller' },
		hash,
	})
}

const handleSupplyContractCreateClick = async (dealNumber: string) => {
	if (isContractCheckBusy.value || isSupplyContractActionBusy.value) {
		return
	}

	const dealId = getDealIdByDealNumber(dealNumber, 'seller')
	if (!dealId) {
		toast.add({
			title: 'Ошибка',
			description: 'Не удалось определить сделку',
			color: 'error',
		})
		return
	}

	selectedSupplyContractDealId.value = dealId
	selectedSupplyContractDealNumber.value = dealNumber
	isContractCheckBusy.value = true

	try {
		const checkOk = await refreshSupplyContractStatus()
		if (!checkOk) {
			return
		}

		if (checkedSupplyContractEntity.value?.id) {
			selectedSupplyContractEntityId.value = checkedSupplyContractEntity.value.id
			isSupplyContractChoiceModalOpen.value = true
			return
		}

		supplyContractType.value = 'supplyContract'
		await editSalesDocument('supplyContract', dealNumber)
	} finally {
		isContractCheckBusy.value = false
	}
}

const handleSupplyContractSelectionChange = (value: unknown) => {
	const numericValue = Number(value)
	selectedSupplyContractEntityId.value =
		Number.isFinite(numericValue) && numericValue > 0 ? numericValue : undefined
}

const handleOpenSupplyContractSelection = () => {
	if (!supplyContractSelectionOptions.value.length) {
		toast.add({
			title: 'Договоры не найдены',
			description: 'Не удалось получить список договоров с этим покупателем',
			color: 'warning',
		})
		return
	}

	selectedSupplyContractEntityId.value = supplyContractSelectionOptions.value[0]?.id
	isSupplyContractChoiceModalOpen.value = false
	isSupplyContractSelectionModalOpen.value = true
}

const handleCancelSupplyContractSelection = () => {
	if (isSupplyContractActionBusy.value) {
		return
	}
	isSupplyContractSelectionModalOpen.value = false
}

const syncSelectedContractAndSpecificationToDeal = (
	deal: Deal,
	contract: SupplyContractSelectionOption,
	spec: SpecificationEntityResponse,
) => {
	deal.supplyContract.entityId = contract.id
	deal.supplyContract.number = contract.number
	deal.supplyContract.entityDate = contract.date
	deal.supplyContract.supplyContractText = contract.termsText
	deal.supplyContract.supplierDetailsCheck = contract.supplierDetailsCheck
	deal.supplyContract.buyerDetailsCheck = contract.buyerDetailsCheck
	deal.supplyContract.coverLetterCheck = contract.coverLetterCheck
	deal.supplyContract.specificationEntityId = spec.id
	deal.supplyContract.specificationNumber = normalizeSpecificationNumber(spec.spec_number)
	deal.supplyContract.specificationDate = spec.spec_date
	deal.supplyContractDate = contract.date
}

const handleCreateSpecificationForSelectedContract = async () => {
	const dealId = selectedSupplyContractDealId.value
	const contractId = selectedSupplyContractEntityId.value

	if (!dealId || !contractId) {
		toast.add({
			title: 'Ошибка',
			description: 'Выберите договор для создания спецификации',
			color: 'error',
		})
		return
	}

	const selectedContract = supplyContractSelectionOptions.value.find((item) => item.id === contractId)
	if (!selectedContract) {
		toast.add({
			title: 'Ошибка',
			description: 'Не удалось найти выбранный договор',
			color: 'error',
		})
		return
	}

	isSupplyContractActionBusy.value = true
	try {
		const spec = await purchasesApi.createSupplySpecification(contractId)
		if (!spec) {
			toast.add({
				title: 'Ошибка',
				description: 'Не удалось создать спецификацию',
				color: 'error',
			})
			return
		}

		await purchasesApi.bindSupplySpecificationToDeal(dealId, spec.id)

		const deal = findDeal(dealId)
		if (deal) {
			syncSelectedContractAndSpecificationToDeal(deal, selectedContract, spec)
		}

		supplyContractType.value = 'specification'
		isSupplyContractChoiceModalOpen.value = false
		isSupplyContractSelectionModalOpen.value = false
		await router.push({
			path: '/profile/editor',
			query: {
				dealId: String(dealId),
				role: 'seller',
			},
			hash: '#supplyContract',
		})
	} catch {
		toast.add({
			title: 'Ошибка',
			description: 'Не удалось создать спецификацию по выбранному договору',
			color: 'error',
		})
	} finally {
		isSupplyContractActionBusy.value = false
	}
}

const handleCreateNewSupplyContractFromChoice = async () => {
	const dealNumber = selectedSupplyContractDealNumber.value
	if (!dealNumber) {
		toast.add({
			title: 'Ошибка',
			description: 'Не удалось определить номер сделки',
			color: 'error',
		})
		return
	}

	isSupplyContractActionBusy.value = true
	try {
		supplyContractType.value = 'supplyContract'
		isSupplyContractChoiceModalOpen.value = false
		await editSalesDocument('supplyContract', dealNumber)
	} finally {
		isSupplyContractActionBusy.value = false
	}
}

const handleSupplyDocumentCreateClick = (dealNumber: string) => {
	selectedSupplyContractDealNumber.value = dealNumber
	supplyDocTypeRadio.value = 'supplyContract'
	isSupplyDocTypeModalOpen.value = true
}

const handleSupplyDocTypeConfirm = async () => {
	const dealNumber = selectedSupplyContractDealNumber.value
	if (!dealNumber) return
	isSupplyDocTypeModalOpen.value = false
	if (supplyDocTypeRadio.value === 'supplyContract') {
		await handleSupplyContractCreateClick(dealNumber)
		return
	}
	const dealId = getDealIdByDealNumber(dealNumber, 'seller')
	const deal = dealId ? findDeal(dealId) : undefined
	if (!hasSupplyContract(deal)) {
		toast.add({
			title: 'В заказе нет выбранных Договоров поставки',
			color: 'warning',
		})
		return
	}
	selectedSupplyContractDealId.value = dealId ?? null
	handleOpenSupplyContractSelection()
}

const handleTransportSelectionChange = (value: unknown) => {
	selectedTransportContractValue.value = value ? String(value) : undefined
}

const handleTransportDocumentCreateClick = (dealNumber: string) => {
	selectedTransportDealNumber.value = dealNumber
	selectedTransportContractValue.value = transportContractSelectionItems.value[0]?.value
	isTransportContractModalOpen.value = true
}

const handleBindTransportContract = async () => {
	const dealId = getDealIdByDealNumber(selectedTransportDealNumber.value, 'seller')
	const number = selectedTransportContractValue.value
	if (!dealId || !number) return
	isTransportActionBusy.value = true
	try {
		await purchasesApi.createTransportContract(dealId, { number })
		const deal = findDeal(dealId)
		if (deal) {
			deal.transportContract = { number, date: new Date().toISOString(), type: 'transport_expedition' }
		}
		isTransportContractModalOpen.value = false
		toast.add({ title: 'Договор перевозки привязан', color: 'success' })
	} catch {
		toast.add({ title: 'Не удалось привязать договор перевозки', color: 'error' })
	} finally {
		isTransportActionBusy.value = false
	}
}

const handleCreateNewTransportContract = async () => {
	const dealId = getDealIdByDealNumber(selectedTransportDealNumber.value, 'seller')
	if (!dealId) return
	isTransportActionBusy.value = true
	try {
		await purchasesApi.createTransportContract(dealId)
		const deal = findDeal(dealId)
		if (deal) {
			deal.transportContract = {
				number: deal.sellerOrderNumber,
				date: new Date().toISOString(),
				type: 'transport_expedition',
			}
		}
		isTransportContractModalOpen.value = false
		openEditor(dealId, 'seller', '#contract')
	} catch {
		toast.add({ title: 'Не удалось создать договор перевозки', color: 'error' })
	} finally {
		isTransportActionBusy.value = false
	}
}

const handleClosingDocumentCreateClick = async (dealNumber: string) => {
	const dealId = getDealIdByDealNumber(dealNumber, type === 'sales' ? 'seller' : 'buyer')
	if (!dealId) return
	if (type === 'purchases') {
		openEditor(dealId, 'buyer', '#accompanyingDocuments')
		return
	}
	try {
		const created = await purchasesApi.createClosingDocument(dealId)
		const deal = findDeal(dealId)
		if (deal && created?.name) {
			const list = [...(deal.closingDocuments as object[] ?? []), created]
			deal.closingDocuments = list
		}
		openEditor(dealId, 'seller', '#accompanyingDocuments')
		toast.add({ title: 'Закрывающий документ создан', color: 'success' })
	} catch {
		toast.add({ title: 'Не удалось создать закрывающий документ', color: 'error' })
	}
}

const renderTz15Cell = (
	docLabel: string | null,
	onView: () => void,
	onCreate: () => void,
	extraLines?: { label: string; onClick: () => void }[],
) => renderTz15DocCell({
	UButton,
	docLabel,
	onView,
	onCreate,
	showCreate: type === 'sales',
	extraLines,
})

const columnsSalesGoodsDeals: TableColumn<any>[] = [
  {
    accessorKey: 'dealNumber',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Заказ`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `№ ${row.getValue('dealNumber')}`,
          class: TABLE_LINK_CLASS,
          onClick: () => {
            editSalesDocument('order', row.getValue('dealNumber'))
          }
        })
    }
  },
  {
    accessorKey: 'date',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Дата`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => normalizeDate(row.getValue('date'))
  },
  {
    accessorKey: 'buyerCompany',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Покупатель`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: `Состояние`,
          icon: isSorted
            ? isSorted === 'asc'
              ? 'i-lucide-arrow-up-narrow-wide'
              : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
          class: '-mx-2.5',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc')
        }
      )
    },
    cell: ({ row }) => {
      const status = row.getValue('status') as string
      const color = {
        Активная: 'text-emerald-600',
        Завершенная: 'text-gray-500'
      }
      return h('span',
        {
          class: `font-semibold ${color[status as keyof typeof color]}`
        },
        status
      )
    }
  },
  {
    accessorKey: 'bill',
    header: 'Счет',
    cell: ({ row }) => {
			const dealNumber = String(row.getValue('dealNumber'))
			const dealId = getDealIdByDealNumber(dealNumber, 'seller')
			const label = row.getValue('bill') as string | null
      return renderTz15Cell(
        label,
        () => {
          clearBillAwaitingFill(dealId)
          openEditor(dealId, 'seller', '#bill')
        },
        () => { void startCreateBill(dealNumber) },
      )
    }
  },
  {
    accessorKey: 'supplyContract',
    header: 'Договор поставки',
    cell: ({ row }) => {
			const dealNumber = String(row.getValue('dealNumber'))
			const dealId = getDealIdByDealNumber(dealNumber, 'seller')
			const label = String(row.getValue('supplyContract') ?? '')
			const docLabel = label && label !== 'Создать договор поставки' ? label : null
      return renderTz15Cell(
        docLabel,
        () => openEditor(dealId, 'seller', '#supplyContract'),
        () => { void handleSupplyDocumentCreateClick(dealNumber) },
      )
    }
  },
  {
    accessorKey: 'transportContract',
    header: 'Договор перевозки',
    cell: ({ row }) => {
      const dealNumber = String(row.getValue('dealNumber'))
      const dealId = getDealIdByDealNumber(dealNumber, 'seller')
      const label = row.getValue('transportContract') as string | null
      return renderTz15Cell(
        label,
        () => openEditor(dealId, 'seller', '#contract'),
        () => { void handleTransportDocumentCreateClick(dealNumber) },
        [{ label: 'Найти транспорт', onClick: () => router.push('/transport-search') }],
      )
    }
  },
  {
    accessorKey: 'closingDocuments',
    header: 'Закрывающие документы',
    cell: ({ row }) => {
      const dealNumber = String(row.getValue('dealNumber'))
      const dealId = getDealIdByDealNumber(dealNumber, 'seller')
      const label = row.getValue('closingDocuments') as string | null
      return renderTz15Cell(
        label,
        () => openEditor(dealId, 'seller', '#accompanyingDocuments'),
        () => { void handleClosingDocumentCreateClick(dealNumber) },
      )
    }
  },
]

const salesContractColumnLegacy: TableColumn<any> = {
    accessorKey: 'contract',
    header: 'Договор',
    cell: ({ row }) => {
			const dealNumber = String(row.getValue('dealNumber'))
			const dealId = getDealIdByDealNumber(dealNumber, 'seller')
			const deal = dealId ? findDeal(dealId) : undefined
			const label = String(row.getValue('contract') ?? '')
			if (!label) {
				return h('span', { class: 'text-neutral-400' }, '—')
			}
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label,
          class: TABLE_LINK_CLASS,
          onClick: () => {
						if (deal?.contractDate) {
							openEditor(dealId, 'seller', '#contract')
						}
          }
        })
    }
  }

const salesInvoiceColumnLegacy: TableColumn<any> = {
    accessorKey: 'invoice',
    header: 'Счет-фактура',
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('invoice'),
          class: TABLE_LINK_CLASS,
          onClick: () => {
            editSalesDocument('invoice', row.getValue('dealNumber'))
          }
        })
    }
  }

const salesOthersColumnLegacy: TableColumn<any> = {
    accessorKey: 'othersDocument',
    header: 'Другие документы',
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('othersDocument'),
          class: TABLE_LINK_CLASS,
          onClick: () => {
            editSalesDocument('othersDocument', row.getValue('dealNumber'))
          }
        })
    }
  }

const salesBillColumnLegacy: TableColumn<any> = {
  accessorKey: 'bill',
  header: 'Счет',
  cell: ({ row }) => {
    const dealNumber = String(row.getValue('dealNumber'))
    return h(UButton, {
      color: 'neutral',
      variant: 'ghost',
      label: row.getValue('bill') || 'Создать счет',
      class: TABLE_LINK_CLASS,
      onClick: () => {
        const label = String(row.getValue('bill') ?? '')
        if (!label) {
          void startCreateBill(dealNumber)
          return
        }
        const dealId = getDealIdByDealNumber(dealNumber, 'seller')
        clearBillAwaitingFill(dealId)
        openEditor(dealId, 'seller', '#bill')
      },
    })
  },
}

const salesActColumn: TableColumn<any> = {
	accessorKey: 'act',
	header: 'Акт',
	cell: ({ row }) => {
		const dealNumber = String(row.getValue('dealNumber'))
		return h(UButton, {
			color: 'neutral',
			variant: 'ghost',
			label: row.getValue('act'),
			class: TABLE_LINK_CLASS,
			onClick: () => {
				void editSalesDocument('act', dealNumber)
			},
		})
	},
}

const columnsSalesServicesDeals: TableColumn<any>[] = [
	...pickColumnsByAccessor(columnsSalesGoodsDeals, [
		'dealNumber',
		'date',
		'buyerCompany',
		'status',
	]),
	salesBillColumnLegacy,
	salesContractColumnLegacy,
	salesActColumn,
	salesInvoiceColumnLegacy,
	salesOthersColumnLegacy,
]

const activeTableColumns = computed(() => {
	if (type === 'purchases') {
		return dealFilter === 'Услуги' ? columnsPurchasesServicesDeals : columnsPurchasesGoodsDeals
	}
	return dealFilter === 'Услуги' ? columnsSalesServicesDeals : columnsSalesGoodsDeals
})

watch(goodsDealsList, () => {
	tablePagination.value = { pageIndex: 0, pageSize: PAGE_SIZE }
  salesTable.value = sortDealsNewestFirst(goodsDealsList.value).map(deal => ({
    dealNumber: deal.sellerOrderNumber || '',
    date: deal.date,
    buyerCompany: deal.buyer.companyName || '',
    status: deal.status,
    bill: formatBillDocLabel(deal),
    supplyContract: formatSupplyContractLabel(deal),
    transportContract: formatTransportDocLabel(deal),
    closingDocuments: formatClosingDocLabel(deal),
    contract: formatContractCellLabel(deal),
    act: formatActCellLabel(deal),
    accompanyingDocuments: formatAccompanyingCellLabel(deal),
    invoice: formatInvoiceCellLabel(deal),
    othersDocument: formatOthersCellLabel(deal),
  }))
}, { immediate: true, deep: true })
</script>