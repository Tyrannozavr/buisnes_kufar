<template>
	<UModal v-model:open="isOpen" title="Выбор продукта из прайса">
		<template #body>
			<div class="space-y-4 p-4">
				<UInput
					v-model="search"
					placeholder="Поиск по названию или артикулу…"
					icon="i-lucide-search"
				/>

				<p v-if="isLoading" class="text-sm text-neutral-500">Загрузка каталога…</p>
				<p v-else-if="!filteredProducts.length" class="text-sm text-neutral-500">
					Нет товаров в каталоге поставщика.
				</p>

				<ul v-else class="max-h-72 overflow-y-auto divide-y border rounded-md">
					<li
						v-for="product in filteredProducts"
						:key="product.id"
						class="p-3 hover:bg-neutral-50 cursor-pointer"
						@click="selectProduct(product)"
					>
						<p class="font-medium text-sm">{{ product.name }}</p>
						<p class="text-xs text-neutral-500">
							Арт. {{ product.article || "—" }} · {{ product.price }} ₽ ·
							{{ product.unit_of_measurement || "шт" }}
						</p>
					</li>
				</ul>
			</div>
		</template>
	</UModal>
</template>

<script setup lang="ts">
import type { ProductResponse } from "~/types/product"
import { useProductsApi } from "~/api/products"

const isOpen = defineModel<boolean>("open", { default: false })

const props = defineProps<{
	sellerCompanyId: number
}>()

const emit = defineEmits<{
	select: [product: ProductResponse]
}>()

const search = ref("")
const products = ref<ProductResponse[]>([])
const isLoading = ref(false)
const productsApi = useProductsApi()

const loadProducts = async () => {
	if (!props.sellerCompanyId) return
	isLoading.value = true
	try {
		const response = await productsApi.getCompanyGoods(props.sellerCompanyId, {
			limit: 200,
		})
		products.value = response.products ?? []
	} catch {
		products.value = []
	} finally {
		isLoading.value = false
	}
}

watch(
	() => [isOpen.value, props.sellerCompanyId] as const,
	([open, companyId]) => {
		if (open && companyId) void loadProducts()
	},
	{ immediate: true },
)

const filteredProducts = computed(() => {
	const query = search.value.trim().toLowerCase()
	if (!query) return products.value
	return products.value.filter((product) => {
		const name = product.name?.toLowerCase() ?? ""
		const article = product.article?.toLowerCase() ?? ""
		return name.includes(query) || article.includes(query)
	})
})

const selectProduct = (product: ProductResponse) => {
	emit("select", product)
	isOpen.value = false
	search.value = ""
}
</script>
