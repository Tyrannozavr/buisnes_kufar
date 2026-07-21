<script setup lang="ts">
import type { ShipmentRequest } from '~/types/transport'
import { useTransportApi } from '~/api/transport'

definePageMeta({
	layout: 'profile',
	title: 'Заявки',
})

const { listRequests, acceptRequest, addRequestFavorite } = useTransportApi()
const toast = useToast()
const requests = ref<ShipmentRequest[]>([])
const loading = ref(false)
const load = async () => {
	loading.value = true
	try { requests.value = await listRequests() }
	catch (e: any) { toast.add({ title: 'Не удалось загрузить заявки', description: e?.message, color: 'error' }) }
	finally { loading.value = false }
}
onMounted(load)
const accept = async (request: ShipmentRequest) => {
	await acceptRequest(request.id)
	toast.add({ title: 'Заявка принята', description: 'Перейти к перевозкам', color: 'success', actions: [{ label: 'Перевозки', onClick: () => navigateTo('/profile/shipments') }] })
	await load()
}
</script>

<template>
	<div class="space-y-5">
		<div><h1 class="text-xl font-semibold">Заявки на перевозку</h1><p class="text-sm text-gray-500">Новые заявки отсортированы первыми.</p></div>
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
					<div class="flex flex-wrap gap-2">
						<UButton variant="soft" label="В избранное" @click="addRequestFavorite(request.id)" />
						<UButton v-if="request.status !== 'accepted'" label="Принять заявку" @click="accept(request)" />
					</div>
				</div>
			</UCard>
		</template>
	</div>
</template>
