<template>
  <UTable 
  sticky 
  :data="type === 'purchases' ? purchasesTable : salesTable" 
  :columns="type === 'purchases' ? columnsPurchasesGoodsDeals : columnsSalesGoodsDeals"
  class="max-h-100 overflow-y-auto overscroll-auto " 
  />
</template>

<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui";
import { normalizeDate } from "~/utils/normalize";
import { useRouter } from "vue-router";
import { useDeals } from "~/composables/useDeals";
import type { Deal } from "~/types/dealState";
import type { BuyerTableItems, SellerTableItems } from "~/types/purchases";
import { usePurchasesApi } from "~/api/purchases";

const { type } = defineProps<{
  type: 'purchases' | 'sales'
}>()

const router = useRouter()
const UButton = resolveComponent('UButton')
const purchasesApi = usePurchasesApi()

const { deals, findDealByDealNumber, findDeal } = useDeals()
const list = deals?.value ?? []

const dealsList: Ref<Deal[]> = computed(() => type === 'purchases' ? list.filter(deal => deal.role === 'buyer') : list.filter(deal => deal.role === 'seller'))
const purchasesTable: Ref<BuyerTableItems[]> = ref([])
const salesTable: Ref<SellerTableItems[]> = ref([])


//purchases
const getDealIdByDealNumber = (dealNumber: string, role: 'buyer' | 'seller'): number | undefined => {
  return findDealByDealNumber(dealNumber, role)?.dealId
}

watch(dealsList, () => {
  purchasesTable.value = [...dealsList.value.map(deal => ({
    dealNumber: deal.buyerOrderNumber || '',
    date: deal.date,
    sellerCompany: deal.seller.companyName || '',
    status: deal.status,
    bill: deal.billDate ? `${deal.bill.number} от ${normalizeDate(deal.billDate)}` : 'Создать счет',
    supplyContract: deal.supplyContractsDate ? `${deal.sellerOrderNumber} от ${normalizeDate(deal.supplyContractsDate)}` : 'Просмотр',
    closingDocuments: deal.closingDocuments?.map((document: any) => document.name).join(', ') || 'Просмотр',
    othersDocument: deal.othersDocuments?.map((document: any) => document.name).join(', ') || 'Просмотр',
  }))]
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
          class: 'text-sky-500 text-wrap',
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
      const billDate = dealId ? findDeal(dealId)?.billDate : undefined
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('bill'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (billDate) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer' },
                hash: '#bill'
              })
						} else {
							useToast().add({
								title: 'Счет пока не создан', 
								color: 'warning',
								icon: 'i-lucide-file-x',
							})
						}
          }
        })
    }
  },
  {
    accessorKey: 'supplyContract',
    header: 'Договор поставки',
    cell: ({ row }) => {
			const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
			const supplyContractDate = dealId ? findDeal(dealId)?.supplyContractsDate : undefined
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('supplyContract'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (supplyContractDate) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer' },
                hash: '#supplyContract'
              })
            } else {
							useToast().add({
								title: 'Договор поставки пока не создан', 
								color: 'warning',
								icon: 'i-lucide-file-x',
							})
						}
          }
        })
    }
  },
  {
    accessorKey: 'closingDocuments',
    header: 'Закрывающие документы',
    cell: ({ row }) => {
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
      const closingDocuments = dealId ? findDeal(dealId) : undefined
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('closingDocuments'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (0) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer' },
                hash: '#accompanyingDocuments'
              })
            } else {
							useToast().add({
								title: 'Нет доступных документов', 
								color: 'warning',
								icon: 'i-lucide-file-x',
							})
						}
          }
        })
    }
  },
  {
    accessorKey: 'othersDocument',
    header: 'Другие документы',
    cell: ({ row }) => {
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'buyer')
      const othersDocuments = dealId ? findDeal(dealId)?.othersDocuments : undefined
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('othersDocument'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (0) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer' },
                hash: '#othersDocument'
              })
            } else {
							useToast().add({
								title: 'Нет доступных документов', 
								color: 'warning',
								icon: 'i-lucide-file-x',
							})
						}
          }
        })
    }
  },
]
////////////////////////////////////////////////////////////

//sales
const editSalesDocument = async (documentType: 'order' | 'bill' | 'supplyContract' | 'closingDocuments' | 'othersDocument', dealNumber: string) => {
  const dealId = getDealIdByDealNumber(dealNumber, 'seller')

  if (dealId) {
    if (documentType === 'order') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller'
        },
        hash: '#order'
      })
    }
    else if (documentType === 'bill') {
      await purchasesApi.createBill(dealId)
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller',
        },
        hash: '#bill'
      })
    } else if (documentType === 'supplyContract') {
      await purchasesApi.createSupplyContract(dealId)
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'sales',
        },
        hash: '#supplyContract'
      })
    } else if (documentType === 'closingDocuments') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller',
        },
        hash: '#closingDocuments'
      })
    } else if (documentType === 'othersDocument') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller',
        },
        hash: '#othersDocument'
      })
    }
  }
}

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
          class: 'text-sky-500 text-wrap',
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
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('bill'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (row.getValue('bill') === 'Создать счет') {
              editSalesDocument('bill', row.getValue('dealNumber'))
            }
          }
        })
    }
  },
  {
    accessorKey: 'supplyContract',
    header: 'Договор поставки',
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('supplyContract'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (row.getValue('supplyContract') === 'Создать договор поставки') {
              editSalesDocument('supplyContract', row.getValue('dealNumber'))
              router.push('/profile/editor#supplyContract')
            }
          }
        })
    }
  },
  {
    accessorKey: 'closingDocuments',
    header: 'Закрывающие документы',
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('closingDocuments'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            editSalesDocument('closingDocuments', row.getValue('dealNumber'))
          }
        })
    }
  },
  {
    accessorKey: 'othersDocument',
    header: 'Другие документы',
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('othersDocument'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            router.push({
              path: '/profile/documents',
              query: { dealId: getDealIdByDealNumber(row.getValue('dealNumber'), 'seller')?.toString() }
            })
          }
        })
    }
  },
]

watch(dealsList, () => {
  salesTable.value = [...dealsList.value.map(deal => ({
    dealNumber: deal.sellerOrderNumber || '',
    date: deal.date,
    buyerCompany: deal.buyer.companyName || '',
    status: deal.status,
    bill: deal.billDate ? `${deal.bill.number} от ${normalizeDate(deal.billDate)}` : 'Создать счет',
    supplyContract: deal.supplyContractsDate ? `Просмотр` : 'Создать договор поставки',
    closingDocuments: deal.closingDocuments?.map((document: any) => document.name).join(', ') || 'Создать',
    othersDocument: deal.othersDocuments?.map((document: any) => document.name).join(', ') || 'Загрузить',
  }))]
}, { immediate: true, deep: true })
</script>