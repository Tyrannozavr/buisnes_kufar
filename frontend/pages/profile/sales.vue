<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-2 ml-4">Продажи</h2>
      <UTabs :items="items" variant="link">

				<!-- <template #product="{ item }">
					<p class="m-3">{{ item.description }}</p>

					<UTable sticky :data="tableDataProduct" :columns="columnsProducts" class="max-h-100 overflow-y-auto overscroll-auto "/>

				</template>
				
				<template #services="{ item }">
					<p class="m-3">{{ item.description }}</p>

					<UTable sticky :data="tableDataServices" :columns="columnsServices" class="max-h-100 overflow-y-auto overscroll-auto "/>
				</template> -->

			</UTabs>
    </div>
  </div>
</template> 

<script setup lang="ts">
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

//Запрос на заказ для продукции
const { data: confirmedProducts , error, refresh, status } = await useLazyFetch('/api/orderedProducts', {
	immediate: true,
	query: {
		sallerId: userCompanyId,
	}
})
console.log(confirmedProducts)
</script>
