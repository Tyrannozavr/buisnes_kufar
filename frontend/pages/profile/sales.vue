<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Продажи</h2>
      <UTabs :items="items" variant="link">

        <template #goods>
          <UTable sticky :data="tableGoods" :columns="columnsGoodsDeals"
            class="max-h-100 overflow-y-auto overscroll-auto " />
        </template>

        <template #services>
          <UTable sticky :data="tableServices" :columns="columnsServicesDeals"
            class="max-h-100 overflow-y-auto overscroll-auto " />
        </template>

      </UTabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TabsItem, TableColumn } from '@nuxt/ui'
import { useSalesStore } from '~/stores/sales'
import type { GoodsDeal, ServicesDeal } from '~/types/dealState'
import type { SellerTableItems } from '~/types/purchases'
import { normalizeDate } from '~/utils/normalize'
import { useRouter } from 'vue-router'
import { usePurchasesApi } from '~/api/purchases'

definePageMeta({
  layout: 'profile'
})

const router = useRouter()
const purchasesApi = usePurchasesApi()
const salesStore = useSalesStore()
const { sales } = storeToRefs(salesStore)
const UButton = resolveComponent('UButton')

//функция создает документ, если его нет и перебрасывает на страницу редактора
const editSalesDocument = async (productType: 'goods' | 'services', documentType: 'order' | 'bill' | 'supplyContract' | 'closingDocuments' | 'othersDocument', dealNumber: string) => {
  let dealId: number | undefined

  if (productType === 'goods') {
    const deal = salesStore.findGoodsDealByDealNumber(dealNumber)
    dealId = deal?.dealId
  } else if (productType === 'services') {
    const deal = salesStore.findServicesDealByDealNumber(dealNumber)
    dealId = deal?.dealId
  }

  if (dealId) {
    //подразумевается, что заказ уже создан и мы перебрасываем на страницу редактора
    if (documentType === 'order') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'sales',
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
          role: 'sales',
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
          role: 'sales',
          productType
        },
        hash: '#closingDocuments'
      })
    } else if (documentType === 'othersDocument') {
      router.push({
        path: '/profile/editor',
        query: {
          dealId: dealId.toString(),
          role: 'sales',
          productType
        },
        hash: '#othersDocument'
      })
    }
  }
}


const items = [
  {
    label: 'Товары',
    description: 'Закладка товары',
    slot: 'goods' as const
  },
  {
    label: 'Услуги',
    description: 'Закладка услуг',
    slot: 'services' as const
  }
] satisfies TabsItem[]

//goods table
const columnsGoodsDeals: TableColumn<any>[] = [
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
          label: row.getValue('bill') === 'Создать счет' ? 'Создать счет' : `${row.getValue('bill')} от ${normalizeDate(row.getValue('date'))}`,
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
          label: row.getValue('supplyContract') === 'Создать договор поставки' ? 'Создать договор поставки' : `${row.getValue('supplyContract')} от ${normalizeDate(row.getValue('date'))}`,
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
            editSalesDocument('goods', 'othersDocument', row.getValue('dealNumber'))
          }
        })
    }
  },
]

//Даем команду на получение и заполнение списка сделок
salesStore.getDeals()

console.log('sales: ', sales.value)

const goodsDeals: GoodsDeal[] = sales.value.goodsDeals
const tableGoods: Ref<SellerTableItems[]> = ref([])

watch(goodsDeals, () => {
  tableGoods.value = [...goodsDeals.map(deal => ({
    dealNumber: deal.sellerOrderNumber || '',
    date: deal.date,
    buyerCompany: deal.buyer.companyName || '',
    status: deal.status,
    bill: deal.bill || 'Создать счет',
    supplyContract: deal.supplyContract || 'Создать договор поставки',
    closingDocuments: deal.closingDocuments || 'Создать закрывающие документы',
    othersDocument: deal.othersDocuments || 'Просмотр',
  }))]
}, { immediate: true, deep: true })

//services table
const columnsServicesDeals: TableColumn<any>[] = [
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
            editSalesDocument('services', 'order', row.getValue('dealNumber'))
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
          label: row.getValue('bill') === 'Создать счет' ? 'Создать счет' : `${row.getValue('bill')} от ${normalizeDate(row.getValue('date'))}`,
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (row.getValue('bill') === 'Создать счет') {
              editSalesDocument('services', 'bill', row.getValue('dealNumber'))
            }
          }
        })
    }
  },
  {
    accessorKey: 'contract',
    header: 'Договор',
    cell: ({ row }) => {
      return h(UButton,
        {
          color: 'neutral',
          variant: 'ghost',
          label: row.getValue('contract') === 'Создать договор' ? 'Создать договор' : `${row.getValue('contract')} от ${normalizeDate(row.getValue('date'))}`,
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            if (row.getValue('contract') === 'Создать договор') {
              editSalesDocument('services', 'supplyContract', row.getValue('dealNumber'))
            }
          }
        })
    }
  },
  {
    accessorKey: 'closingDocuments',
    header: 'Закрывающие документы',
    cell: ({ row }) => {
      return h('a', { href: '/profile/contracts/editor#closingDocuments', class: 'text-sky-500 text-wrap' }, row.getValue('closingDocuments'))
    }
  },
  {
    accessorKey: 'othersDocument',
    header: 'Другие документы',
    cell: ({ row }) => {
      return h('a', { href: '/profile/contracts/editor#othersDocument', class: 'text-sky-500 text-wrap' }, row.getValue('othersDocument'))
    }
  }
]

const servicesDeals: ServicesDeal[] = sales.value.servicesDeals
const tableServices: Ref<SellerTableItems[]> = ref([])

watch(servicesDeals, () => {
  tableServices.value = [...servicesDeals.map(service => ({
    dealNumber: service.sellerOrderNumber || '',
    date: service.date,
    buyerCompany: service.buyer.companyName || '',
    status: service.status,
    bill: service.bill || 'Создать счет',
    contract: service.contract || 'Создать договор',
    closingDocuments: service.closingDocuments || 'Создать закрывающие документы',
    othersDocument: service.othersDocuments || 'Просмотр',
  }))]
}, { immediate: true, deep: true })
</script>
