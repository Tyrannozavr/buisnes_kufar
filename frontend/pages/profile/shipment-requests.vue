<script setup lang="ts">
import type { ShipmentRequest } from '~/types/transport'
import { useTransportApi } from '~/api/transport'
import { useFavoriteToggle } from '~/composables/useFavoriteToggle'

definePageMeta({
	layout: 'profile',
	title: 'Заявки',
})

const {
	listRequests,
	acceptRequest,
	listRequestFavoriteIds,
	addRequestFavorite,
	removeRequestFavorite,
} = useTransportApi()
const toast = useToast()
const requests = ref<ShipmentRequest[]>([])
const loading = ref(false)
const acceptPendingId = ref<number | null>(null)

const {
	pendingId: favoritePendingId,
	isFavorite,
	loadFavoriteIds,
	toggleFavorite,
} = useFavoriteToggle({
	list: listRequestFavoriteIds,
	add: addRequestFavorite,
	remove: removeRequestFavorite,
	addedTitle: 'Заявка добавлена в избранное',
	removedTitle: 'Заявка убрана из избранного',
})

const load = async () => {
	loading.value = true
	try {
		const [list] = await Promise.all([listRequests(), loadFavoriteIds()])
		requests.value = list
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить заявки', description: e?.message, color: 'error' })
	} finally {
		loading.value = false
	}
}

onMounted(load)

const accept = async (request: ShipmentRequest) => {
	if (acceptPendingId.value === request.id) return
	acceptPendingId.value = request.id
	try {
		await acceptRequest(request.id)
		requests.value = requests.value.map(item =>
			item.id === request.id ? { ...item, status: 'accepted', is_highlighted: false } : item,
		)
		toast.add({
			title: 'Заявка принята',
			description: 'Перейти к перевозкам',
			color: 'success',
			actions: [{ label: 'Перевозки', onClick: () => navigateTo('/profile/shipments') }],
		})
	} catch (e: any) {
		toast.add({
			title: 'Не удалось принять заявку',
			description: e?.data?.detail || e?.message,
			color: 'error',
		})
	} finally {
		acceptPendingId.value = null
	}
}
</script>

<template>
	<div class="space-y-5">
		<div>
			<h1 class="text-xl font-semibold">Заявки на перевозку</h1>
			<p class="text-sm text-gray-500">Новые заявки отсортированы первыми.</p>
		</div>
		<div v-if="loading" class="text-sm text-gray-500">Загрузка…</div>
		<p v-else-if="!requests.length" class="text-sm text-gray-500">Заявок пока нет.</p>
		<template v-else>
			<UCard
				v-for="request in requests"
				:key="request.id"
				:class="request.is_highlighted ? 'bg-yellow-50 border-yellow-200' : ''"
			>
				<div class="flex flex-col sm:flex-row justify-between gap-3">
					<div>
						<p class="font-medium">Заявка № {{ request.id }} · {{ request.status }}</p>
						<p class="text-sm text-gray-600">
							{{ request.search_filters?.from_locations?.map(x => x.name).join(', ') || '—' }}
							→
							{{ request.search_filters?.to_locations?.map(x => x.name).join(', ') || '—' }}
						</p>
						<p class="text-sm text-gray-500">
							Вес: {{ request.search_filters?.cargo_weight_kg || '—' }} кг
							· объём: {{ request.search_filters?.cargo_volume_m3 || '—' }} м³
						</p>
					</div>
					<div class="flex flex-col items-stretch sm:items-end gap-2 shrink-0">
						<UButton
							v-if="request.status !== 'accepted'"
							label="Принять заявку"
							:loading="acceptPendingId === request.id"
							class="cursor-pointer"
							@click="accept(request)"
						/>
						<FavoriteToggleButton
							:active="isFavorite(request.id)"
							:loading="favoritePendingId === request.id"
							@click="toggleFavorite(request.id)"
						/>
					</div>
				</div>
			</UCard>
		</template>
	</div>
</template>
