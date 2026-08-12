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

const {
	deleteOpen,
	deleteLoading,
	deleteTitle,
	deleteMessage,
	deleteConfirmLabel,
	askDelete,
	confirmDelete,
} = useConfirmDelete()

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

const removeRequest = (id: number) => {
	askDelete({
		message: `Точно хотите удалить заявку № ${id} из избранного?`,
		confirmLabel: 'Удалить',
		onConfirm: async () => {
			await removeRequestFavorite(id)
			await load()
		},
	})
}

const removeVehicle = (vehicle: TransportVehicleResult) => {
	askDelete({
		message: `Точно хотите удалить «${vehicle.name}» из избранного?`,
		confirmLabel: 'Удалить',
		onConfirm: async () => {
			await removeVehicleFavorite(vehicle.id)
			await load()
		},
	})
}
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
				<div class="flex items-start justify-between gap-3">
					<div class="min-w-0">
						<p class="font-medium">Заявка № {{ request.id }} · {{ request.status }}</p>
						<p class="text-sm">
							{{ loc(request.search_filters?.from_locations) }}
							→
							{{ loc(request.search_filters?.to_locations) }}
						</p>
					</div>
					<UButton
						icon="i-heroicons-trash"
						size="sm"
						variant="soft"
						color="error"
						label="Удалить"
						class="cursor-pointer shrink-0 self-start"
						@click="removeRequest(request.id)"
					/>
				</div>
			</UCard>
		</div>

		<div v-else>
			<p v-if="!vehicles.length" class="text-sm text-gray-500">Нет избранного транспорта.</p>
			<UCard v-for="vehicle in vehicles" :key="vehicle.id" class="mb-3">
				<div class="flex items-start justify-between gap-3">
					<div class="space-y-1 min-w-0">
						<p class="font-medium">
							{{ vehicle.name }}
							<span v-if="vehicle.plate_number" class="text-gray-500 font-normal"> · {{ vehicle.plate_number }}</span>
							<span v-if="vehicle.trailer_plate_number" class="text-gray-500 font-normal"> · п/п {{ vehicle.trailer_plate_number }}</span>
						</p>
						<p class="text-sm text-gray-600">
							{{ vehicle.company?.type || 'Перевозчик' }} «{{ vehicle.company?.name }}»
						</p>
						<p class="text-sm text-gray-600">
							{{ loc(vehicle.from_locations) }} → {{ loc(vehicle.to_locations) }}
						</p>
						<p class="text-sm text-gray-500">
							<span v-if="vehicle.capacity_tons != null">{{ vehicle.capacity_tons }} т</span>
							<span v-if="vehicle.body_type">{{ vehicle.capacity_tons != null ? ', ' : '' }}{{ vehicle.body_type }}</span>
							<span v-if="vehicle.volume_m3 != null"> · {{ vehicle.volume_m3 }} м³</span>
							<span v-if="vehicle.loading_methods?.length">, {{ vehicle.loading_methods.join(', ') }}</span>
						</p>
						<p v-if="vehicle.adr_classes?.length" class="text-sm text-gray-500">
							ADR: {{ vehicle.adr_classes.join(', ') }}
						</p>
						<p v-if="vehicle.partial_load" class="text-sm text-amber-700">Догруз</p>
					</div>
					<UButton
						icon="i-heroicons-trash"
						size="sm"
						variant="soft"
						color="error"
						label="Удалить"
						class="cursor-pointer shrink-0 self-start"
						@click="removeVehicle(vehicle)"
					/>
				</div>
			</UCard>
		</div>

		<ConfirmDeleteModal
			v-model:open="deleteOpen"
			:title="deleteTitle"
			:message="deleteMessage"
			:loading="deleteLoading"
			:confirm-label="deleteConfirmLabel"
			@confirm="confirmDelete"
		/>
	</div>
</template>
