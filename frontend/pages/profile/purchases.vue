<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Закупки</h2>
      <UTabs :items="items" variant="link">

        <template #goods="{ item }">
          <UTable sticky :data="tableGoods" :columns="columnsGoodsDeals"
            class="max-h-100 overflow-y-auto overscroll-auto " />
        </template>

        <template #services="{ item }">
          <UTable sticky :data="tableServices" :columns="columnsServicesDeals"
            class="max-h-100 overflow-y-auto overscroll-auto " />
        </template>

      </UTabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TabsItem, TableColumn } from '@nuxt/ui'
import { usePurchasesStore } from '~/stores/purchases'
import type { GoodsDeal, ServicesDeal } from '~/types/dealState'
import type { BuyerTableItems } from '~/types/purchases'
import { normalizeDate } from '~/utils/normalize'
import { useRouter } from 'vue-router'
import { usePurchasesApi } from '~/api/purchases'

definePageMeta({
  layout: 'profile'
})

const router = useRouter()
const purchasesApi = usePurchasesApi()
const purchasesStore = usePurchasesStore()
const { purchases } = storeToRefs(purchasesStore)
const UButton = resolveComponent('UButton')


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
            router.push('/profile/documents')
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
    accessorKey: 'sallerCompany',
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
    cell: ({ row }) => row.getValue('sallerCompany')
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
            router.push('/profile/documents')
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
            router.push('/profile/documents')
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
            router.push('/profile/documents')
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
            router.push('/profile/documents')
          }
        })
    }
  },
]

//Даем команду на получение и заполнение списка сделок
purchasesStore.getDeals()

console.log('purchases: ', purchases.value)

const goodsDeals: GoodsDeal[] = purchases.value.goodsDeals
const tableGoods: Ref<BuyerTableItems[]> = ref([])

watch(goodsDeals, () => {
  tableGoods.value = [...goodsDeals.map(deal => ({
    dealNumber: deal.buyerOrderNumber || '',
    date: deal.date,
    sallerCompany: deal.saller.companyName || '',
    status: deal.status,
    bill: 'Просмотр',
    supplyContract: 'Просмотр',
    closingDocuments: 'Просмотр',
    othersDocument: 'Просмотр',
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
            router.push('/profile/documents')
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
    accessorKey: 'sallerCompany',
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
            router.push('/profile/documents')
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
          label: row.getValue('contract'),
          class: 'text-sky-500 text-wrap',
          onClick: () => {
            router.push('/profile/documents')
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
            router.push('/profile/documents')
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
            router.push('/profile/documents')
          }
        })
    }
  }
]

const servicesDeals: ServicesDeal[] = purchases.value.servicesDeals
const tableServices: Ref<BuyerTableItems[]> = ref([])

watch(servicesDeals, () => {
  tableServices.value = [...servicesDeals.map(service => ({
    dealNumber: service.buyerOrderNumber || '',
    date: service.date,
    sallerCompany: service.saller.companyName || '',
    status: service.status,
    bill: 'Просмотр',
    contract: 'Просмотр',
    closingDocuments: 'Просмотр',
    othersDocument: 'Просмотр',
  }))]
}, { immediate: true, deep: true })
</script>
