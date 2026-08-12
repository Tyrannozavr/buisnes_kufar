<script setup lang="ts">
import type { TransportDictionaries, TransportSearchFilters, TransportVehicleResult } from '~/types/transport'
import { useTransportApi } from '~/api/transport'
import { navigateToChatById } from '~/composables/chat'
import { useFavoriteToggle } from '~/composables/useFavoriteToggle'

useHead({ title: 'Поиск транспорта — TradeSynergy' })

const toast = useToast()
const { search, getDictionaries, addVehicleFavorite, removeVehicleFavorite, listVehicleFavoriteIds, sendVehicleRequest } = useTransportApi()
const pending = ref(false)
const searched = ref(false)
const messagePending = ref(false)
const dictionaries = ref<TransportDictionaries>({ body_types: [], loading_methods: [], adr_classes: [] })
const vehicles = ref<TransportVehicleResult[]>([])
const contacts = ref<TransportVehicleResult | null>(null)
const contactsOpen = ref(false)
const filters = ref<TransportSearchFilters>({
	body_types: [], loading_methods: [], adr_classes: [], partial_load: false,
	from_locations: [], to_locations: [],
})
const locations = ref({ from: '', to: '' })

const {
	pendingId: favoritePendingId,
	isFavorite,
	loadFavoriteIds,
	toggleFavorite,
} = useFavoriteToggle({
	list: listVehicleFavoriteIds,
	add: addVehicleFavorite,
	remove: removeVehicleFavorite,
	addedTitle: 'Транспорт добавлен в избранное',
	removedTitle: 'Транспорт убран из избранного',
})

const onSearch = async () => {
	pending.value = true
	try {
		const payload = {
			...filters.value,
			from_locations: locations.value.from.split(',').map(name => name.trim()).filter(Boolean).map(name => ({ name })),
			to_locations: locations.value.to.split(',').map(name => name.trim()).filter(Boolean).map(name => ({ name })),
		}
		const result = await search(payload)
		vehicles.value = result.vehicles
		searched.value = true
		await loadFavoriteIds()
		const created = result.requests_created ?? 0
		if (created > 0) {
			toast.add({
				title: 'Заявка отправлена перевозчикам',
				description: created === 1
					? 'Пассивная заявка создана у перевозчика. Ожидайте отклика или выберите ТС ниже.'
					: `Пассивные заявки созданы у ${created} перевозчиков. Ожидайте отклика или выберите ТС ниже.`,
				color: 'success',
			})
		}
	} catch (e: any) {
		toast.add({ title: 'Не удалось выполнить поиск', description: e?.data?.detail || e?.message, color: 'error' })
	} finally { pending.value = false }
}

onMounted(async () => {
	try {
		dictionaries.value = await getDictionaries()
	} catch {
		// словари необязательны для выдачи списка
	}
	await onSearch()
})

const showContacts = (vehicle: TransportVehicleResult) => {
	contacts.value = vehicle
	contactsOpen.value = true
}
const sendRequest = async (vehicle: TransportVehicleResult) => {
	try {
		await sendVehicleRequest(vehicle.id)
		toast.add({ title: 'Заявка отправлена перевозчику', color: 'success' })
	} catch (e: any) {
		toast.add({ title: 'Не удалось отправить заявку', description: e?.data?.detail || e?.message, color: 'error' })
	}
}

const writeMessage = async (vehicle: TransportVehicleResult) => {
	if (!vehicle.company?.id) {
		toast.add({ title: 'Не удалось открыть чат', description: 'Нет id компании перевозчика', color: 'error' })
		return
	}
	messagePending.value = true
	try {
		await navigateToChatById(vehicle.company.id)
		contactsOpen.value = false
	} catch (e: any) {
		toast.add({
			title: 'Не удалось открыть чат',
			description: e?.data?.detail || e?.message || 'Попробуйте позже',
			color: 'error',
		})
	} finally {
		messagePending.value = false
	}
}

const loc = (items?: { name?: string }[]) => (items || []).map(x => x.name).filter(Boolean).join(', ') || '—'

const formatDate = (value?: string | null) => {
	if (!value) return null
	const d = new Date(value)
	return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString('ru-RU')
}

const trailerSize = (vehicle: TransportVehicleResult) => {
	const parts = [vehicle.trailer_length_m, vehicle.trailer_width_m, vehicle.trailer_height_m]
		.filter((v): v is number => v != null)
	if (!parts.length) return null
	return `${parts.join('×')} (Д×Ш×В)`
}

const companyTitle = (vehicle: TransportVehicleResult) => {
	const type = vehicle.company.type?.trim()
	const name = vehicle.company.name?.trim() || 'Перевозчик'
	if (type && !name.startsWith(type)) return `${type} «${name}»`
	return name
}
</script>

<template>
	<div class="container mx-auto px-4 py-8 max-w-5xl">
		<div class="mb-6">
			<h1 class="text-2xl font-semibold text-gray-900">Поиск транспорта</h1>
			<p class="mt-1 text-sm text-gray-600">Подберите транспорт по маршруту, типу кузова и параметрам груза.</p>
		</div>
		<UCard class="mb-6" :ui="{ body: 'p-4 pb-3 sm:p-4 sm:pb-3' }">
			<form class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" @submit.prevent="onSearch">
				<UFormField label="Откуда">
					<UInput v-model="locations.from" placeholder="Города через запятую" class="w-full" />
				</UFormField>
				<UFormField label="Куда">
					<UInput v-model="locations.to" placeholder="Города через запятую" class="w-full" />
				</UFormField>
				<UFormField label="Тип кузова">
					<USelectMenu
						v-model="filters.body_types"
						:items="dictionaries.body_types"
						multiple
						placeholder="Выберите тип"
					/>
				</UFormField>
				<UFormField label="Способы загрузки">
					<USelectMenu
						v-model="filters.loading_methods"
						:items="dictionaries.loading_methods"
						multiple
						placeholder="Выберите способы"
					/>
				</UFormField>
				<UFormField label="Классы ADR">
					<USelectMenu
						v-model="filters.adr_classes"
						:items="dictionaries.adr_classes"
						multiple
						placeholder="Выберите классы"
					/>
				</UFormField>
				<UFormField label="Дата загрузки">
					<UInput v-model="filters.load_date" type="date" class="w-full" />
				</UFormField>
				<UFormField :label="filters.partial_load ? 'Вес догруза, кг' : 'Вес груза, кг'">
					<UInput v-model.number="filters.cargo_weight_kg" type="number" class="w-full" />
				</UFormField>
				<UFormField :label="filters.partial_load ? 'Объём догруза, м³' : 'Объём груза, м³'">
					<UInput v-model.number="filters.cargo_volume_m3" type="number" step="0.1" class="w-full" />
				</UFormField>
				<div class="flex flex-wrap items-center justify-between gap-3 sm:col-span-2 lg:col-span-3">
					<UCheckbox v-model="filters.partial_load" label="Частичная загрузка" />
					<UButton type="submit" :loading="pending" label="Найти транспорт" class="cursor-pointer" />
				</div>
			</form>
		</UCard>
		<p v-if="searched && !pending" class="mb-3 text-sm text-green-600">
			Найдено ТС: {{ vehicles.length }}
		</p>
		<div v-if="pending" class="text-sm text-gray-500 py-8">Загрузка…</div>
		<div v-else-if="!searched" class="text-sm text-gray-500 py-8">Загрузка списка транспорта…</div>
		<div v-else-if="!vehicles.length" class="text-sm text-gray-500 py-8">
			По заданным параметрам транспорт не найден (свой парк в выдаче не показывается).
		</div>
		<ul v-else class="space-y-3">
			<li
				v-for="vehicle in vehicles"
				:key="vehicle.id"
				class="border border-gray-200 rounded-lg p-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
			>
				<div class="min-w-0 space-y-1">
					<p class="font-medium text-gray-900">
						{{ vehicle.name }}
						<span v-if="vehicle.plate_number" class="text-gray-500 font-normal"> · {{ vehicle.plate_number }}</span>
						<span v-if="vehicle.trailer_plate_number" class="text-gray-500 font-normal"> · п/п {{ vehicle.trailer_plate_number }}</span>
					</p>
					<p class="text-sm text-gray-600">
						{{ companyTitle(vehicle) }}
					</p>
					<p class="text-sm text-gray-600">
						{{ loc(vehicle.from_locations) }} → {{ loc(vehicle.to_locations) }}
						<span v-if="formatDate(vehicle.load_date)"> · {{ formatDate(vehicle.load_date) }}</span>
					</p>
					<p class="text-sm text-gray-500">
						<span v-if="vehicle.capacity_tons != null">{{ vehicle.capacity_tons }} т</span>
						<span v-if="vehicle.body_type">{{ vehicle.capacity_tons != null ? ', ' : '' }}{{ vehicle.body_type }}</span>
						<span v-if="vehicle.volume_m3 != null"> · {{ vehicle.volume_m3 }} м³</span>
						<span v-if="vehicle.loading_methods?.length">, {{ vehicle.loading_methods.join(', ') }}</span>
					</p>
					<p v-if="trailerSize(vehicle)" class="text-sm text-gray-500">
						{{ trailerSize(vehicle) }}
					</p>
					<p v-if="vehicle.adr_classes?.length" class="text-sm text-gray-500">
						ADR: {{ vehicle.adr_classes.join(', ') }}
					</p>
					<p v-if="vehicle.partial_load" class="text-sm text-amber-700">
						Догруз
						<span v-if="vehicle.partial_load_weight_kg != null"> · {{ vehicle.partial_load_weight_kg }} кг</span>
						<span v-if="vehicle.partial_load_volume_m3 != null"> · {{ vehicle.partial_load_volume_m3 }} м³</span>
					</p>
				</div>
				<div class="flex flex-wrap gap-2 shrink-0">
					<UButton
						color="neutral"
						variant="soft"
						label="Показать контакты"
						class="cursor-pointer"
						@click="showContacts(vehicle)"
					/>
					<FavoriteToggleButton
						:active="isFavorite(vehicle.id)"
						:loading="favoritePendingId === vehicle.id"
						@click="toggleFavorite(vehicle.id)"
					/>
					<UButton
						color="primary"
						variant="soft"
						label="Отправить заявку"
						class="cursor-pointer"
						@click="sendRequest(vehicle)"
					/>
				</div>
			</li>
		</ul>

		<UModal v-model:open="contactsOpen">
			<template #content>
				<UCard v-if="contacts">
					<template #header>
						<span class="font-medium">{{ companyTitle(contacts) }}</span>
					</template>
					<p>ИНН: {{ contacts.company.inn || '—' }}</p>
					<p>Адрес: {{ contacts.company.legal_address || '—' }}</p>
					<p>Телефон: {{ contacts.company.phone || '—' }}</p>
					<p>Email: {{ contacts.company.email || '—' }}</p>
					<div class="mt-4 flex flex-wrap gap-2">
						<UButton label="Отправить заявку" @click="sendRequest(contacts)" />
						<UButton
							variant="soft"
							label="Написать сообщение"
							:loading="messagePending"
							@click="writeMessage(contacts)"
						/>
					</div>
				</UCard>
			</template>
		</UModal>
	</div>
</template>
