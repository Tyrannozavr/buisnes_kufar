<script setup lang="ts">
import { useTransportApi } from '~/api/transport'
import { isLogisticsTradeActivity } from '~/types/company'
import type { ShipmentRequest, TransportVehicleResult } from '~/types/transport'

definePageMeta({
	layout: 'profile',
	title: 'Избранное',
})

const { $api } = useNuxtApp()
const {
	listRequestFavorites,
	listVehicleFavorites,
	removeRequestFavorite,
	removeVehicleFavorite,
} = useTransportApi()
const toast = useToast()
const isLogistics = ref(false)
const requests = ref<ShipmentRequest[]>([])
const vehicles = ref<TransportVehicleResult[]>([])

const load = async () => {
	try {
		const company = await $api.get('/v1/company/me') as { trade_activity?: string }
		isLogistics.value = isLogisticsTradeActivity(company.trade_activity)
		if (isLogistics.value) {
			requests.value = await listRequestFavorites() as unknown as ShipmentRequest[]
		} else {
			vehicles.value = await listVehicleFavorites() as unknown as TransportVehicleResult[]
		}
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить избранное', description: e?.message, color: 'error' })
	}
}

onMounted(load)

const loc = (items?: { name?: string }[]) => (items || []).map(x => x.name).filter(Boolean).join(', ') || '—'
</script>

<template>
	<div class="space-y-5">
		<div>
			<h1 class="text-xl font-semibold">Избранное</h1>
			<p class="text-sm text-gray-500">
				{{ isLogistics ? 'Сохранённые заявки на перевозку.' : 'Сохранённый транспорт.' }}
			</p>
		</div>

		<div v-if="isLogistics">
			<p v-if="!requests.length" class="text-sm text-gray-500">Нет избранных заявок.</p>
			<UCard v-for="request in requests" :key="request.id" class="mb-3">
				<div class="flex justify-between gap-3">
					<div>
						<p class="font-medium">Заявка № {{ request.id }} · {{ request.status }}</p>
						<p class="text-sm">
							{{ loc(request.search_filters?.from_locations) }}
							→
							{{ loc(request.search_filters?.to_locations) }}
						</p>
					</div>
					<UButton
						variant="ghost"
						color="error"
						label="Убрать"
						@click="removeRequestFavorite(request.id).then(load)"
					/>
				</div>
			</UCard>
		</div>

		<div v-else>
			<p v-if="!vehicles.length" class="text-sm text-gray-500">Нет избранного транспорта.</p>
			<UCard v-for="vehicle in vehicles" :key="vehicle.id" class="mb-3">
				<div class="flex justify-between gap-3">
					<div>
						<p class="font-medium">
							{{ vehicle.name }}
							<span v-if="vehicle.plate_number" class="text-gray-500 font-normal"> · {{ vehicle.plate_number }}</span>
						</p>
						<p class="text-sm text-gray-500">
							{{ vehicle.company?.type }} «{{ vehicle.company?.name }}»
							· {{ loc(vehicle.from_locations) }} → {{ loc(vehicle.to_locations) }}
							<span v-if="vehicle.capacity_tons != null"> · {{ vehicle.capacity_tons }} т</span>
							<span v-if="vehicle.body_type"> · {{ vehicle.body_type }}</span>
						</p>
					</div>
					<UButton
						variant="ghost"
						color="error"
						label="Убрать"
						@click="removeVehicleFavorite(vehicle.id).then(load)"
					/>
				</div>
			</UCard>
		</div>
	</div>
</template>
