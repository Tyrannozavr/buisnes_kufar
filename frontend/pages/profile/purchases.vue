<template>
  <div class="max-w-full">
    <div class="bg-white shadow rounded-lg pt-4">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Закупки</h2>
      <UTabs :items="items" variant="link">

				<template #product="{ item }">
					<p class="m-3">{{ item.description }}</p>

					<UTable sticky :data="tableDataProduct" :columns="columnsProducts" class="max-h-100 overflow-y-auto overscroll-auto " />

				</template>
				
				<template #services="{ item }">
					<p class="m-3">{{ item.description }}</p>

					<UTable sticky :data="tableDataServices" :columns="columnsServices" class="max-h-100 overflow-y-auto overscroll-auto "/>
				</template>

			</UTabs>
    </div>
  </div>
</template> 

<script setup lang="ts">
//доделать таблицу
//как-то передать даныне из checkout - отдельное состояние ?
import type { TabsItem, TableColumn } from '@nuxt/ui'
import { useUserStore } from '~/stores/user'
const userCompanyId = useUserStore().companyId

definePageMeta({
	layout: 'profile'
})

const items = [
	{
		label: 'Товары',
		description: 'Закладка товары',
		slot: 'product' as const
	},
	{
		label: 'Услуги',
		description: 'Закладка услуг',
		slot: 'services' as const
	}
] satisfies TabsItem[]

const columnsProducts: TableColumn<any>[] = [
{accessorKey: 'productNumber', header: 'Заказ'},
{accessorKey: 'date', header: 'Дата'},
{accessorKey: 'saller', header: 'Поставщик'},
{accessorKey: 'state', header: 'Состояние'},
{accessorKey: 'bill', header: 'Счет'},
{accessorKey: 'supplyContract', header: 'Договор поставки'},
{accessorKey: 'accompanyingDocuments', header: 'Сопродительные документы'},
{accessorKey: 'invoice', header: 'Счет-фактура'},
{accessorKey: 'othersDocument', header: 'Другие документы'},
]

const tableDataProduct = [
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
	{
		productNumber: '04443',
		date: '7.04.25',
		saller: 'Продажник_1',
		state: 'Завершенная',
		bill: 'Просмотр',
		supplyContract: 'Просмотр',
		accompanyingDocuments: 'Просмотр',
		invoice: 'Просмотр',
		othersDocument: 'Просмотр',
	},
]

const columnsServices: TableColumn<any>[] = [
{accessorKey: 'productNumber', header: 'Заказ'},
{accessorKey: 'date', header: 'Дата'},
{accessorKey: 'saller', header: 'Поставщик'},
{accessorKey: 'state', header: 'Состояние'},
{accessorKey: 'bill', header: 'Счет'},
{accessorKey: 'contract', header: 'Договор'},
{accessorKey: 'act', header: 'акт'},
{accessorKey: 'invoice', header: 'Счет-фактура'},
{accessorKey: 'othersDocument', header: 'Другие документы'}
]

const tableDataServices = [{
	productNumber: '04443',
	date: '7.04.25',
	saller: 'Продажник_1',
	state: 'Завершенная',
	bill: 'Просмотр',
	contract: 'Просмотр',
	act: 'Просмотр',
	invoice: 'Просмотр',
	othersDocument: 'Просмотр',
}]

// //Запрос на заказанную продукцию
// const { data: confirmedProducts , error, refresh, status } = await useLazyFetch('/api/orderedProducts', {
// 	immediate: true,
// 	query: {
// 		clientId: userCompanyId,
// 	}
// })
// console.log(confirmedProducts)


</script>


