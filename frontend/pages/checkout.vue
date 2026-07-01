<template>
	<div>
		<h1 class="text-3xl font-bold mb-8">Оформление заказа</h1>

		<div v-if="!cartStore.items.length" class="text-center py-12">
			<UIcon name="i-heroicons-shopping-cart" class="h-16 w-16 mx-auto text-gray-400 mb-4" />
			<h2 class="text-xl font-medium text-gray-900 mb-2">Корзина пуста</h2>
			<p class="text-gray-500 mb-6">Добавьте товары в корзину, чтобы оформить заказ</p>

			<div class="space-x-3">
				<UButton to="/catalog/products" color="primary">
					Перейти в каталог товаров
				</UButton>
				<UButton to="/catalog/services" color="primary">
					Перейти в каталог услуг
				</UButton>
			</div>
		</div>

		<div
			v-for="group in orderGroups"
			:key="group.key"
			class="mb-15 bg-neutral-50 shadow-sm rounded-lg p-8 px-16 m-5 mt-0"
		>
			<h2 class="text-xl font-semibold mb-4">
				{{ groupHeading(group) }}
			</h2>

			<UTable sticky :data="group.items" :columns="columns" />
			<p class="mt-3">{{ itemsCountLabel(group) }} — {{ group.items.length }}</p>
			<p>
				На сумму —
				<span class="font-bold">{{ productsAmount(group.items).toLocaleString('ru-RU') }} ₽</span>
			</p>

			<div class="flex space-x-3 mt-3 mb-5">
				<UButton
					v-if="userStore.isAuthenticated"
					color="primary"
					:loading="submittingGroupKey === group.key"
					:disabled="Boolean(submittingGroupKey && submittingGroupKey !== group.key)"
					@click.prevent="handleOrderSubmit(group)"
				>
					Подтвердить
				</UButton>
				<UButton v-else color="primary" to="/auth/login">
					Войти для оформления
				</UButton>
				<UButton
					color="neutral"
					variant="soft"
					:disabled="Boolean(submittingGroupKey)"
					@click.prevent="removeItemsFromCart(group.items)"
				>
					{{ returnToCartLabel(group) }}
				</UButton>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { useCartStore } from '~/stores/cart'
import { useUserStore } from '~/stores/user'
import type { TableColumn } from '@nuxt/ui'
import type {
	CheckoutOrderGroup,
	CheckoutOrderType,
	ProductInCheckout,
} from '~/types/product'
import { ref, type Ref, watch } from 'vue'
import { useCreateOrderFromCheckoutQuery } from '~/queries/purchases'

const userStore = useUserStore()
const cartStore = useCartStore()
const products = cartStore.items
const orderGroups: Ref<CheckoutOrderGroup[]> = ref([])
const submittingGroupKey = ref<string | null>(null)
const toast = useToast()
const { orderFromCheckout } = useCreateOrderFromCheckoutQuery()

const orderTypeFromProductType = (type: string): CheckoutOrderType =>
	type === 'Услуга' ? 'Услуги' : 'Товары'

const groupHeading = (group: CheckoutOrderGroup): string => {
	if (group.orderType === 'Услуги') {
		return `Заказ на оказание услуг для «${group.companyName}»`
	}
	return `Заказ на поставку товаров для «${group.companyName}»`
}

const itemsCountLabel = (group: CheckoutOrderGroup): string =>
	group.orderType === 'Услуги' ? 'Всего услуг' : 'Всего товаров'

const returnToCartLabel = (group: CheckoutOrderGroup): string =>
	group.orderType === 'Услуги' ? 'Вернуть услуги в корзину' : 'Вернуть товары в корзину'

const handleOrderSubmit = async (group: CheckoutOrderGroup): Promise<void> => {
	if (!group.items?.length) return

	submittingGroupKey.value = group.key
	try {
		const response = await orderFromCheckout(group.items)
		if (!response?.deals?.[0]) {
			toast.add({
				title: 'Не удалось оформить заказ',
				description: 'Проверьте, что позиции есть в каталоге, и попробуйте снова.',
				color: 'error',
			})
			return
		}
		removeItemsFromCart(group.items)
		showToast(group.orderType)
	} catch {
		toast.add({
			title: 'Ошибка оформления',
			description: 'Не удалось создать заказ. Попробуйте ещё раз.',
			color: 'error',
		})
	} finally {
		submittingGroupKey.value = null
	}
}

const buildOrderGroups = (cartItems: typeof products): void => {
	const groups = new Map<string, CheckoutOrderGroup>()
	const companyNames = new Map<number, string>()

	cartItems.forEach((item) => {
		if (item.product.company_id && item.product.company_name) {
			companyNames.set(item.product.company_id, item.product.company_name)
		}
	})

	cartItems.forEach((item) => {
		const productType = item.product.type === 'Услуга' ? 'Услуга' : 'Товар'
		const orderType = orderTypeFromProductType(productType)
		const companyId = item.product.company_id
		const key = `${companyId}-${orderType}`

		const product: ProductInCheckout = {
			slug: item.product.slug,
			description: item.product.description,
			logoUrl: item.product.logo_url,
			productName: item.product.name,
			article: item.product.article != null ? String(item.product.article) : '',
			productType,
			quantity: item.quantity,
			units: item.product.unit_of_measurement,
			price: item.product.price,
			amount: Number(item.quantity) * Number(item.product.price),
		}

		const existing = groups.get(key)
		if (existing) {
			existing.items.push(product)
			return
		}

		const companyName =
			item.product.company_name ||
			companyNames.get(companyId) ||
			'Поставщик'

		groups.set(key, {
			key,
			companyId,
			companyName,
			orderType,
			items: [product],
		})
	})

	orderGroups.value = Array.from(groups.values())
}

watch(
	() => products,
	(newValue) => {
		buildOrderGroups(newValue)
	},
	{ deep: true, immediate: true },
)

const columns: TableColumn<ProductInCheckout>[] = reactive([
	{
		header: '№',
		cell: ({ row }) => row.index + 1,
	},
	{ accessorKey: 'productName', header: 'Название' },
	{ accessorKey: 'article', header: 'Артикул' },
	{ accessorKey: 'quantity', header: 'Количество' },
	{ accessorKey: 'units', header: 'Ед. изм.' },
	{ accessorKey: 'price', header: 'Цена, ₽' },
	{
		accessorKey: 'amount',
		header: () => h('div', { class: 'text-right' }, 'Общая стоимость, ₽'),
		cell: ({ row }) => h('div', { class: 'text-right' }, row.getValue('amount')),
	},
])

const productsAmount = (items: ProductInCheckout[]): number =>
	items.reduce((acc, product) => acc + product.amount, 0)

const removeItemsFromCart = (items: ProductInCheckout[]): void => {
	items.forEach((product) => cartStore.removeFromCart(product.slug))
}

const showToast = (orderType: CheckoutOrderType) => {
	const description =
		orderType === 'Услуги'
			? 'Заказ на услуги подтверждён и появится в Закупках'
			: 'Заказ на товары подтверждён и появится в Закупках'

	toast.add({
		title: 'Готово',
		description,
		color: 'success',
		actions: [{
			icon: 'i-lucide-arrow-right',
			label: 'Перейти к закупкам',
			color: 'success',
			variant: 'link',
			to: '/profile/purchases',
		}],
	})
}
</script>
