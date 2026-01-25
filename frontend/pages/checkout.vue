<template>
	<div>
		<h1 class="text-3xl font-bold mb-8">Оформление заказа</h1>

		<div v-if="!cartStore.items.length" class="text-center py-12">
      <UIcon name="i-heroicons-shopping-cart" class="h-16 w-16 mx-auto text-gray-400 mb-4"/>
      <h2 class="text-xl font-medium text-gray-900 mb-2">Корзина пуста</h2>
      <p class="text-gray-500 mb-6">Добавьте товары в корзину, чтобы оформить заказ</p>
			
			<div class="space-x-3">
				<UButton
						to="/catalog/products"
						color="primary"
				>
					Перейти в каталог товаров
				</UButton>
				<UButton
						to="/catalog/services"
						color="primary"
				>
					Перейти в каталог услуг
				</UButton>
			</div>
    </div>

		<div v-for="cp in companiesAndProducts" :key="cp.companyId" class="mb-15 bg-neutral-50 shadow-sm rounded-lg p-8 px-16 m-5 mt-0">
			
			<h2>Заказ на поставку для <span>"{{ cp.companyName }}"</span></h2>
			
			<div class="flex-row space-y-5 mb-10">
				<div v-if="cp.products[0]">
					<UTable sticky :data="cp.products" :columns="columns"/>
					
					<p>Всего товаров - {{ cp.products.length }}</p>
					<p>На сумму - <span class="font-bold">{{ productsAmount(cp.products).toLocaleString('ru-RU') }} ₽</span></p>
		
					<div class="flex space-x-3 mt-3 mb-5">
						<UButton
                v-if="userStore.isAuthenticated"
                color="primary"
                to="/checkout"
								@click="
								postProducts(cp.products),
								messageToSaller(cp.companyId,cp.products),
								showToast(),
								removeItemsFromCart(cp.products)"
            >
              Оформить заказ
            </UButton>
            <UButton
                v-else
                color="primary"
                to="/auth/login"
            >
              Войти для оформления
            </UButton>
            <UButton
                color="neutral"
                variant="soft"
                @click="removeItemsFromCart(cp.products)"
            >
              Очистить корзину
            </UButton>
					</div>
				</div>


				<div v-if="cp.services[0]">
					<UTable sticky :data="cp.services" :columns="columns"/>
					
					<p>Количество услуг - {{ cp.services.length }}</p>
					<p>На сумму - <span class="font-bold">{{ productsAmount(cp.services).toLocaleString('ru-RU') }} ₽</span></p>
		
					<div class="flex space-x-3 mt-3 mb-10">
						<UButton
                v-if="userStore.isAuthenticated"
                color="primary"
                to=""
								@click="
								postProducts(cp.services),
								messageToSaller(cp.companyId,cp.services),
								showToast(),
								removeItemsFromCart(cp.services)"
            >
              Оформить заказ
            </UButton>
            <UButton
                v-else
                color="primary"
                to="/auth/login"
            >
              Войти для оформления
            </UButton>
            <UButton
                color="neutral"
                variant="soft"
                @click="removeItemsFromCart(cp.services)"
            >
              Очистить корзину
            </UButton>
					</div>
				</div>
			</div>

		</div>
	</div>			
</template>

<script setup lang="ts">
import { useCartStore } from '~/stores/cart'
import { useUserStore } from '~/stores/user'
import type { TableColumn } from '@nuxt/ui'
import type { CompaniesAndProducts, ProductInCheckout } from 'types/product'
import { ref, type Ref, watch } from 'vue'
import { useChatsApi } from '~/api/chats'

const { createChat, sendMessage } = useChatsApi()

const userStore = useUserStore()
const buyer: {companyId: number, companyName: string, companySlug: string} = {
	companyId: userStore.companyId,
	companyName: userStore.companyName,
	companySlug: userStore.companySlug,
}

const cartStore = useCartStore()
const products = cartStore.items


let companiesAndProducts: Ref<CompaniesAndProducts[]> = ref([])

watch(() => products, (newValue) => {
	
	companiesAndProducts = ref([])
	sortProducts(newValue)
	console.log(companiesAndProducts.value)
	
}, {deep: true})


const sortProducts = (products: any[]): void  => {

	products.forEach(item => {

		const ProductInCheckout = companiesAndProducts.value.find((el: CompaniesAndProducts) => el.companyId === item.product.company_id)
		//have Id
		if (ProductInCheckout) {
			//type = product
			if (item.product.type === 'Товар')
			{
				ProductInCheckout!.products.push(
					{
					slug: item.product.slug,
					description: item.product.description,
					logoUrl: item.product.logo_url,
					type: item.product.type,
					position: ProductInCheckout!.products.length + 1,
					productName: item.product.name,
					article: Number(item.product.article),
					quantity: item.quantity,
					units: item.product.unit_of_measurement,
					price: item.product.price,
					amount: Number(item.quantity)*Number(item.product.price)
			})
			}
			//type = service
			else {
				ProductInCheckout!.services.push(
					{
					slug: item.product.slug,
					description: item.product.description,
					logoUrl: item.product.logo_url,
					type: item.product.type,
					position: ProductInCheckout!.services.length + 1,
					productName: item.product.name,
					article: Number(item.product.article),
					quantity: item.quantity,
					units: item.product.unit_of_measurement,
					price: item.product.price,
					amount: Number(item.quantity)*Number(item.product.price)
			})
			}
		}
		// no Id
		else {
			//create products
			if (item.product.type === 'Товар') 
			{
				companiesAndProducts.value.push(
				{
				companyId: item.product.company_id,
				companyName: item.product.company_name,
				services: [],
				products: [{
					slug: item.product.slug,
					description: item.product.description,
					logoUrl: item.product.logo_url,
					type: item.product.type,
					position: 1,
					productName: item.product.name,
					article: Number(item.product.article),
					quantity: item.quantity,
					units: item.product.unit_of_measurement,
					price: item.product.price,
					amount: Number(item.quantity)*Number(item.product.price)
				}]
			})
			} 
			//create services
			else {
				companiesAndProducts.value.push(
				{
				companyId: item.product.company_id,
				companyName: item.product.company_name,
				services: [{
					slug: item.product.slug,
					description: item.product.description,
					logoUrl: item.product.logo_url,
					type: item.product.type,
					position: 1,
					productName: item.product.name,
					article: Number(item.product.article),
					quantity: item.quantity,
					units: item.product.unit_of_measurement,
					price: item.product.price,
					amount: Number(item.quantity)*Number(item.product.price)
				}],
				products: []
			})
			}
		}
	})
	console.log(companiesAndProducts)
}

sortProducts(products)

const columns: TableColumn<ProductInCheckout>[] = reactive([
  { accessorKey: 'position', header: '№'},
  { accessorKey: 'productName', header: 'Название' },
  { accessorKey: 'article', header: 'Артикль' },
  { accessorKey: 'quantity', header: 'Количество' },
  { accessorKey: 'units', header: 'Ед.Изм.' },
  { accessorKey: 'price', header: 'Цена, ₽' },
  { accessorKey: 'amount', header: () => h('div', {class: 'text-right'}, 'Общая стоимость, ₽'),
		cell: ({row}) => h('div',{class: 'text-right'}, row.getValue('amount'))
	 }
])

const productsAmount = (products: ProductInCheckout[]): number => {
	const amount = products.reduce((acc: number, product: any) => acc + product.amount, 0)
	return amount
}	

const removeItemsFromCart = (items: ProductInCheckout[]): void => {
	const itemsForRemove: string[] = []
	items.forEach(product => {
		itemsForRemove.push(product.slug)
	})
	itemsForRemove.forEach(slug => cartStore.removeFromCart(slug))
}

//отправляем продукцию на сервер 
const postProducts = async (product: ProductInCheckout[]) => {
	$fetch('/api/orderedProducts', {
		method: 'POST',
		body: {
			product,
			buyer
		}
	})
}

//отправляем сообщение продавцу о намерении совершить заказ
const messageToSaller = async (companyId: number , product: ProductInCheckout[]): Promise<void> =>  {
	const response = await createChat({participantId: companyId})
	const productList: string[] = []
	product.forEach(prod => productList.push(prod.productName))
	sendMessage(response.id, {senderId: companyId, content: `Здравуствуйте, хочу приобрести у вас следующую продукцию: ${productList}`})
}

//всплывающее уведомление
const toast = useToast()
const showToast = () => {
	toast.add({
		title: 'Готово',
		description: 'Заказ отправлен на оформление',
		color: 'success',
		actions: [{
			icon: 'i-lucide-arrow-right',
			label: 'Перейти к закупкам',
			color: 'success',
			variant: 'link',
			to: '/profile/purchases'
		}]
	}
	)
}
</script>