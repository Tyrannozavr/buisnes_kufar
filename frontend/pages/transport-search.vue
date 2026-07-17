<script setup lang="ts">
import type { CompanyShort } from '~/types/company'
import { useCompaniesApi } from '~/api/companies'
import CustomPagination from '~/components/ui/CustomPagination.vue'
import { usePurchasesApi } from '~/api/purchases'
import { useDeals } from '~/composables/useDeals'

useHead({ title: 'Поиск транспорта — TradeSynergy' })

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { searchServiceProviders } = useCompaniesApi()
const purchasesApi = usePurchasesApi()
const { refreshDealFromServer, findDeal } = useDeals({ role: 'seller' })

const dealId = computed(() => {
	const raw = route.query.deal
	const n = Number(Array.isArray(raw) ? raw[0] : raw)
	return Number.isFinite(n) && n > 0 ? n : null
})

const search = ref(typeof route.query.search === 'string' ? route.query.search : '')
const currentPage = ref(1)
const perPage = 12
const pending = ref(false)
const companies = ref<CompanyShort[]>([])
const pagination = ref({ total: 0, page: 1, perPage: 12, totalPages: 1 })

const load = async () => {
	pending.value = true
	try {
		const res = await searchServiceProviders({
			search: search.value.trim() || undefined,
			page: currentPage.value,
			perPage,
		})
		companies.value = (res?.data ?? []) as CompanyShort[]
		pagination.value = res?.pagination ?? { total: 0, page: 1, perPage, totalPages: 1 }
	} catch (e: any) {
		toast.add({
			title: 'Не удалось загрузить перевозчиков',
			description: e?.message || '',
			color: 'error',
		})
		companies.value = []
	} finally {
		pending.value = false
	}
}

onMounted(load)
watch(currentPage, load)

const onSearch = async () => {
	currentPage.value = 1
	await router.replace({
		query: {
			...(dealId.value ? { deal: String(dealId.value) } : {}),
			...(search.value.trim() ? { search: search.value.trim() } : {}),
		},
	})
	await load()
}

const selectCarrier = async (company: CompanyShort) => {
	if (!dealId.value) {
		await navigateTo(`/companies/${company.slug}`)
		return
	}
	try {
		const number = `TE-${company.id}-${dealId.value}`
		await purchasesApi.createTransportContract(dealId.value, { number })
		// Store сделок кэшируется: без refresh колонка перевозки остаётся пустой.
		const refreshed = await refreshDealFromServer(dealId.value)
		if (!refreshed) {
			const deal = findDeal(dealId.value)
			if (deal) {
				deal.transportContract = {
					number,
					date: new Date().toISOString(),
					type: 'transport_expedition',
				}
			}
		}
		toast.add({
			title: 'Перевозчик выбран',
			description: `${company.name}: договор экспедиции № ${number}`,
			color: 'success',
		})
		await navigateTo(`/profile/sales`)
	} catch (e: any) {
		toast.add({
			title: 'Не удалось привязать перевозчика к сделке',
			description: e?.data?.detail || e?.message || '',
			color: 'error',
		})
	}
}
</script>

<template>
	<div class="container mx-auto px-4 py-8 max-w-5xl">
		<div class="mb-6">
			<h1 class="text-2xl font-semibold text-gray-900">Поиск транспорта</h1>
			<p class="mt-1 text-sm text-gray-600">
				Перевозчики и экспедиторы платформы.
				<span v-if="dealId">Выберите компанию, чтобы привязать договор перевозки к сделке № {{ dealId }}.</span>
				<span v-else>Откройте карточку компании или вернитесь из Продаж по ссылке «Найти транспорт».</span>
			</p>
		</div>

		<form class="flex flex-col sm:flex-row gap-2 mb-6" @submit.prevent="onSearch">
			<UInput
				v-model="search"
				class="flex-1"
				placeholder="Название, город, ИНН…"
				icon="i-heroicons-magnifying-glass"
			/>
			<UButton type="submit" color="primary" :loading="pending" label="Найти" />
		</form>

		<div v-if="pending" class="text-sm text-gray-500 py-8">Загрузка…</div>
		<div v-else-if="!companies.length" class="text-sm text-gray-500 py-8">
			Ничего не найдено. Измените запрос или проверьте, что в системе есть компании с ролью Перевозчик/Экспедитор.
		</div>
		<ul v-else class="space-y-3">
			<li
				v-for="c in companies"
				:key="c.id"
				class="border border-gray-200 rounded-lg p-4 flex flex-col sm:flex-row sm:items-center gap-3 justify-between"
			>
				<div>
					<p class="font-medium text-gray-900">{{ c.name }}</p>
					<p class="text-sm text-gray-500">
						{{ c.trade_activity || 'Перевозчик' }}
						<span v-if="c.city"> · {{ c.city }}</span>
						<span v-if="c.inn"> · ИНН {{ c.inn }}</span>
					</p>
				</div>
				<div class="flex gap-2 shrink-0">
					<UButton
						:to="`/companies/${c.slug}`"
						color="neutral"
						variant="soft"
						label="Карточка"
					/>
					<UButton
						color="primary"
						:label="dealId ? 'Выбрать для сделки' : 'Открыть'"
						@click="selectCarrier(c)"
					/>
				</div>
			</li>
		</ul>

		<div v-if="pagination.totalPages > 1" class="mt-6">
			<CustomPagination
				:current-page="currentPage"
				:total="pagination.total"
				:per-page="perPage"
				@update:page="(p) => { currentPage = p }"
			/>
		</div>
	</div>
</template>
