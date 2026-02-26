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
				<div v-if="cp.goods[0]">
					<UTable sticky :data="cp.goods" :columns="columns"/>
					
					<p>Всего товаров - {{ cp.goods.length }}</p>
					<p>На сумму - <span class="font-bold">{{ productsAmount(cp.goods).toLocaleString('ru-RU') }} ₽</span></p>
		
					<div class="flex space-x-3 mt-3 mb-5">
						<UButton
                v-if="userStore.isAuthenticated"
                color="primary"
                to="/checkout"
								@click.prevent="handleOrderSubmit(cp, cp.goods)"
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
                @click="removeItemsFromCart(cp.goods)"
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
								@click.prevent="handleOrderSubmit(cp, cp.services)"
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
import type { Buyer, CompaniesAndProducts, ProductInCheckout } from 'types/product'
import { ref, type Ref, watch } from 'vue'
import { useChatsApi } from '~/api/chats'
import { usePurchasesApi } from '~/api/purchases'
import { useCompaniesApi } from '~/api/companies'

const { createChat, sendMessage } = useChatsApi()
const { getCompanyById } = useCompaniesApi()
const userStore = useUserStore()
const cartStore = useCartStore()
const products = cartStore.items
const { createOrderFromCheckout } = usePurchasesApi()
const companiesAndProducts: Ref<CompaniesAndProducts[]> = ref([])
const toast = useToast()

const companySlugCache = new Map<number, string>()
const handleGetCompanySlug = async (companyId: number): Promise<string | null> => {
	const cachedSlug = companySlugCache.get(companyId)
	if (cachedSlug) return cachedSlug

	try {
		const company = await getCompanyById(companyId, true)
		const slug = company?.slug
		if (!slug) return null
		companySlugCache.set(companyId, slug)
		return slug
	} catch {
		return null
	}
}

const handleCreateOrder = async (cp: CompaniesAndProducts, items: ProductInCheckout[]): Promise<void> => {
	if (!items?.length) return

	const companySlug = await handleGetCompanySlug(cp.companyId)
	if (!companySlug) return

	await createOrderFromCheckout(items, {
		companyId: cp.companyId,
		companyName: cp.companyName,
		companySlug,
	} as Buyer)
}

const handleOrderSubmit = async (cp: CompaniesAndProducts, items: ProductInCheckout[]): Promise<void> => {
	await handleCreateOrder(cp, items)
	await messageToSaller(cp.companyId, items)
	removeItemsFromCart(items)
	showToast()
}

const sortProducts = (products: any[]): void  => {
  products.forEach(item => {
    const product: ProductInCheckout = {
      slug: item.product.slug,
      description: item.product.description,
      logoUrl: item.product.logo_url,
      type: item.product.type,
      productName: item.product.name,
      article: Number(item.product.article),
      quantity: item.quantity,
      units: item.product.unit_of_measurement,
      price: item.product.price,
      amount: Number(item.quantity) * Number(item.product.price)
    }

    const companyProducts: CompaniesAndProducts | undefined = companiesAndProducts.value.find((el: CompaniesAndProducts) => el.companyId === item.product.company_id)
    if (companyProducts) {
      const products: ProductInCheckout[] = item.product.type === 'Товар' ? companyProducts?.goods : companyProducts?.services
      products?.push(product)
    } else {
      companiesAndProducts.value.push({
        companyId: item.product.company_id,
        companyName: item.product.company_name,
        goods: item.product.type === 'Товар' ? [product] : [],
        services: item.product.type === 'Услуга' ? [product] : [],
      })
    }
	})
}

watch(() => products, (newValue) => {
  companiesAndProducts.value = []
  sortProducts(newValue)
}, { deep: true, immediate: true })


const columns: TableColumn<ProductInCheckout>[] = reactive([
  {
    header: '№',
    cell: ({row}) => row.index + 1 
  },
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

const messageToSaller = async (companyId: number, product: ProductInCheckout[]): Promise<void> => {
	try {
		const chatData = await createChat({ participantId: companyId })
		if (!chatData?.id) return
		const productList = product.map((p) => p.productName).join(', ')
		await sendMessage(chatData.id, {
			content: `Здравствуйте, хочу приобрести у вас следующую продукцию: ${productList}. Перейти на страницу заказа: /checkout`,//FIXME: добавить ссылку на страницу заказа в редакторе 
		})
	} catch (err) {
		console.error('Ошибка при создании чата/отправке сообщения:', err)
	}
}

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