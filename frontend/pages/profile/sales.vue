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

definePageMeta({
	layout: 'profile'
})

const salesStore = useSalesStore()
const { sales } = storeToRefs(salesStore)

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

const UButton = resolveComponent('UButton')
//goods table
const columnsGoodsDeals: TableColumn<any>[] = [
	{
		accessorKey: 'dealNumber',
		header: ({column}) => {
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
		cell: ({ row }) => `№ ${row.getValue('dealNumber')}`
	},
	{ 
		accessorKey: 'date', 
		header: ({column}) => {
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
	},
	{ 
		accessorKey: 'buyerCompany', 
		header: ({column}) => {
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
		header: ({column}) => {
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
			return h('a', { href: '/profile/contracts/editor#bill', class: 'text-sky-500 text-wrap' }, row.getValue('bill'))
		}
	},
	{
		accessorKey: 'supplyContract',
		header: 'Договор поставки',
		cell: ({ row }) => {
			return h('a', { href: '/profile/contracts/editor#supplyContract', class: 'text-sky-500 text-wrap' }, row.getValue('supplyContract'))
		}
	},
	{
		accessorKey: 'closingDocuments',
		header: 'Закрывающие документы',
		cell: ({ row }) => {
			return h('a', { href: '/profile/contracts/editor#closingDocuments', class: 'text-sky-500 text-wrap' }, row.getValue('closingDocuments'))
		}
	},
	// {
	// 	accessorKey: 'invoice',
	// 	header: 'Счет-фактура',
	// 	cell: ({ row }) => {
	// 		return h('a', { href: '/profile/contracts/editor#invoice', class: 'text-sky-500 text-wrap' }, row.getValue('invoice'))
	// 	}
	// },
	{
		accessorKey: 'othersDocument',
		header: 'Другие документы',
		cell: ({ row }) => {
			return h('a', { href: '/profile/contracts/editor#othersDocument', class: 'text-sky-500 text-wrap' }, row.getValue('othersDocument'))
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
    buyerCompany: deal.buyer.name,
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
		header: ({column}) => {
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
		cell: ({ row }) => `№ ${row.getValue('dealNumber')}`
	},
	{
		accessorKey: 'date',
		header: ({column}) => {
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
	},
	{
		accessorKey: 'buyerCompany',
		header: ({column}) => {
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
		header: ({column}) => {
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
			return h('a', { href: '/profile/contracts/editor#bill', class: 'text-sky-500 text-wrap' }, row.getValue('bill'))
		}
	},
	{
		accessorKey: 'contract',
		header: 'Договор',
		cell: ({ row }) => {
			return h('a', { href: '/profile/contracts/editor#contract', class: 'text-sky-500 text-wrap' }, row.getValue('contract'))
		}
	},
	{
		accessorKey: 'closingDocuments',
		header: 'Закрывающие документы',
		cell: ({ row }) => {
			return h('a', { href: '/profile/contracts/editor#closingDocuments', class: 'text-sky-500 text-wrap' }, row.getValue('closingDocuments'))
		}
	},
	// {
	// 	accessorKey: 'invoice',
	// 	header: 'Счет-фактура',
	// 	cell: ({ row }) => {
	// 		return h('a', { href: '/profile/contracts/editor#invoice', class: 'text-sky-500 text-wrap' }, row.getValue('invoice'))
	// 	}
	// },
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
    buyerCompany: service.buyer.name,
    status: service.status,
    bill: service.bill || 'Создать счет',
    contract: service.contract || 'Создать договор',
    closingDocuments: service.closingDocuments || 'Создать закрывающие документы',
    othersDocument: service.othersDocuments || 'Просмотр',
  }))]
}, { immediate: true, deep: true })
</script>
