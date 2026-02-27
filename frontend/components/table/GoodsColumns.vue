<template>
  <UTable 
  sticky 
  :data="type === 'purchases' ? tablePurchasesGoods : tableSalesGoods" 
  :columns="type === 'purchases' ? columnsPurchasesGoodsDeals : columnsSalesGoodsDeals"
  class="max-h-100 overflow-y-auto overscroll-auto " 
  />
</template>

<script setup lang="ts">
import { storeToRefs } from "pinia";
import type { TableColumn } from "@nuxt/ui";
import { normalizeDate } from "~/utils/normalize";
import { useRouter } from "vue-router";
import { usePurchasesStore } from "~/stores/purchases";
import { useSalesStore } from "~/stores/sales";
import type { GoodsDeal } from "~/types/dealState";
import type { BuyerTableItems, SellerTableItems } from "~/types/purchases";
import { usePurchasesApi } from "~/api/purchases";

const { type } = defineProps<{
  type: 'purchases' | 'sales'
}>()

const router = useRouter()
const UButton = resolveComponent('UButton')
const purchasesApi = usePurchasesApi()

const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const { purchases } = storeToRefs(purchasesStore)
const { sales } = storeToRefs(salesStore)

const goodsDeals: Ref<GoodsDeal[]> = computed(() => type === 'purchases' ? purchases.value.goodsDeals : sales.value.goodsDeals)
const tablePurchasesGoods: Ref<BuyerTableItems[]> = ref([])
const tableSalesGoods: Ref<SellerTableItems[]> = ref([])


//purchases
const getDealIdByDealNumber = (dealNumber: string, productType: 'goods' | 'services'): number | undefined => {
  const store = type === 'purchases' ? purchasesStore : salesStore
  if (productType === 'goods') {
    return store.findGoodsDealByDealNumber(dealNumber)?.dealId
  } else if (productType === 'services') {
    return store.findGoodsDealByDealNumber(dealNumber)?.dealId
  }
  return undefined
}

watch(goodsDeals, () => {
  tablePurchasesGoods.value = [...goodsDeals.value.map(deal => ({
    dealNumber: deal.buyerOrderNumber || '',
    date: deal.date,
    sellerCompany: deal.seller.companyName || '',
    status: deal.status,
    bill: deal.billNumber ? `${deal.billNumber} от ${normalizeDate(deal.billDate || '')}` : 'Просмотр',
    supplyContract: deal.supplyContractNumber ? `${deal.supplyContractNumber} от ${normalizeDate(deal.supplyContractDate || '')}` : 'Просмотр',
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
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'goods')
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
                query: { dealId: String(dealId), role: 'buyer', productType: 'goods' },
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
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'goods')
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('bill'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (dealId != null) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer', productType: 'goods' },
                hash: '#bill'
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
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'goods')
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('supplyContract'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (dealId != null) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer', productType: 'goods' },
                hash: '#supplyContract'
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
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'goods')
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('closingDocuments'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (dealId != null) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer', productType: 'goods' },
                hash: '#accompanyingDocuments'
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
      const dealId = getDealIdByDealNumber(row.getValue('dealNumber'), 'goods')
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('othersDocument'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (dealId != null) {
              router.push({
                path: '/profile/editor',
                query: { dealId: String(dealId), role: 'buyer', productType: 'goods' },
                hash: '#othersDocument'
              })
            }
          }
        })
    }
  },
]
////////////////////////////////////////////////////////////

//sales
const editSalesDocument = async (productType: 'goods' | 'services', documentType: 'order' | 'bill' | 'supplyContract' | 'closingDocuments' | 'othersDocument', dealNumber: string) => {
  const dealId = getDealIdByDealNumber(dealNumber, productType)

  if (dealId) {
    if (documentType === 'order') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller',
          productType
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
          productType
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
          productType
        },
        hash: '#supplyContract'
      })
    } else if (documentType === 'closingDocuments') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller',
          productType
        },
        hash: '#closingDocuments'
      })
    } else if (documentType === 'othersDocument') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'seller',
          productType
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
            editSalesDocument('goods', 'order', row.getValue('dealNumber'))
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
              editSalesDocument('goods', 'bill', row.getValue('dealNumber'))
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
              editSalesDocument('goods', 'supplyContract', row.getValue('dealNumber'))
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
            editSalesDocument('goods', 'closingDocuments', row.getValue('dealNumber'))
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
              query: { dealId: getDealIdByDealNumber(row.getValue('dealNumber'), 'goods')?.toString() }
            })
          }
        })
    }
  },
]

watch(goodsDeals, () => {
  tableSalesGoods.value = [...goodsDeals.value.map(deal => ({
    dealNumber: deal.sellerOrderNumber || '',
    date: deal.date,
    buyerCompany: deal.buyer.companyName || '',
    status: deal.status,
    bill: deal.billNumber || 'Создать счет',
    supplyContract: deal.supplyContractNumber || 'Создать договор поставки',
    closingDocuments: deal.closingDocuments?.map((document: any) => document.name).join(', ') || 'Создать',
    othersDocument: deal.othersDocuments?.map((document: any) => document.name).join(', ') || 'Загрузить',
  }))]
}, { immediate: true, deep: true })
</script>