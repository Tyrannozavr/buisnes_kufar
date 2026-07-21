<script setup lang="ts">
import type { CargoData, Shipment } from '~/types/transport'
import type { CompanyDriver, CompanyVehicle } from '~/types/fleet'
import { useTransportApi } from '~/api/transport'
import { useFleetApi } from '~/api/me/fleet'
definePageMeta({
	layout: 'profile',
	title: 'Перевозки',
})

const { $api } = useNuxtApp()
const { listShipments, updateCargo, updateTransport, updateDeal } = useTransportApi()
const { listVehicles, listDrivers } = useFleetApi()
const toast = useToast()
const myCompanyId = ref<number | null>(null)
const shipments = ref<Shipment[]>([])
const vehicles = ref<CompanyVehicle[]>([])
const drivers = ref<CompanyDriver[]>([])
const selected = ref<Shipment | null>(null)
const cargoOpen = ref(false)
const transportOpen = ref(false)
const cargo = ref<CargoData>({})
const transport = ref({ vehicle_id: null as number | null, driver_id: null as number | null })
const cargoFields: { key: keyof CargoData, label: string, type?: string }[] = [
	{ key: 'loading_date', label: 'Дата загрузки', type: 'date' }, { key: 'loading_time', label: 'Время загрузки' }, { key: 'loading_address', label: 'Адрес загрузки' },
	{ key: 'unloading_date', label: 'Дата выгрузки', type: 'date' }, { key: 'unloading_time', label: 'Время выгрузки' }, { key: 'unloading_address', label: 'Адрес выгрузки' },
	{ key: 'route', label: 'Маршрут' }, { key: 'cargo_name', label: 'Наименование груза' }, { key: 'transport_conditions', label: 'Условия перевозки' },
	{ key: 'net_weight', label: 'Вес нетто, кг', type: 'number' }, { key: 'gross_weight', label: 'Вес брутто, кг', type: 'number' }, { key: 'places_count', label: 'Количество мест', type: 'number' },
	{ key: 'volume', label: 'Объём, м³', type: 'number' }, { key: 'marking', label: 'Маркировка' }, { key: 'packaging_type', label: 'Тип упаковки' },
	{ key: 'packaging', label: 'Упаковка' }, { key: 'seal', label: 'Пломба' }, { key: 'rate', label: 'Ставка', type: 'number' },
	{ key: 'payment_terms', label: 'Условия оплаты' }, { key: 'declared_value', label: 'Объявленная ценность', type: 'number' }, { key: 'identity_document_requisites', label: 'Реквизиты документа' },
]
const isClient = computed(() => selected.value != null && selected.value.client_company_id === myCompanyId.value)
const load = async () => {
	try {
		const company = await $api.get('/v1/company/me') as { id: number }
		myCompanyId.value = company.id
		shipments.value = await listShipments()
		;[vehicles.value, drivers.value] = await Promise.all([listVehicles(), listDrivers()])
	} catch (e: any) { toast.add({ title: 'Не удалось загрузить перевозки', description: e?.message, color: 'error' }) }
}
onMounted(load)
const openCargo = (shipment: Shipment) => { selected.value = shipment; cargo.value = { ...shipment.cargo_data }; cargoOpen.value = true }
const openTransport = (shipment: Shipment) => { selected.value = shipment; transport.value = { vehicle_id: shipment.vehicle_id || null, driver_id: shipment.driver_id || null }; transportOpen.value = true }
const saveCargo = async () => { if (selected.value) { await updateCargo(selected.value.id, cargo.value); cargoOpen.value = false; await load(); toast.add({ title: 'Данные груза сохранены', color: 'success' }) } }
const saveTransport = async () => { if (selected.value) { await updateTransport(selected.value.id, transport.value); transportOpen.value = false; await load(); toast.add({ title: 'Транспорт назначен', color: 'success' }) } }
const linkDeal = async (shipment: Shipment) => {
	const id = Number(window.prompt('Введите ID активного заказа продажи'))
	if (Number.isFinite(id) && id > 0) { await updateDeal(shipment.id, id); await load() }
}
</script>

<template>
	<div class="space-y-5">
		<div><h1 class="text-xl font-semibold">Перевозки</h1><p class="text-sm text-gray-500">Данные груза редактирует клиент, транспорт назначает перевозчик.</p></div>
		<div class="overflow-x-auto border rounded-lg">
			<table class="min-w-full text-sm"><thead class="bg-gray-50"><tr><th class="p-3 text-left">Заказ</th><th class="p-3 text-left">Дата</th><th class="p-3 text-left">Контрагент</th><th class="p-3 text-left">Договор</th><th class="p-3 text-left">Груз</th><th class="p-3 text-left">Транспорт</th><th class="p-3 text-left">К заказу клиента</th></tr></thead>
				<tbody><tr v-for="shipment in shipments" :key="shipment.id" class="border-t"><td class="p-3">№ {{ shipment.number }}/{{ shipment.year }}</td><td class="p-3">{{ new Date(shipment.created_at).toLocaleDateString() }}</td><td class="p-3">{{ shipment.client_company_id === myCompanyId ? `Перевозчик #${shipment.carrier_company_id}` : `Клиент #${shipment.client_company_id}` }}</td><td class="p-3">Позже</td><td class="p-3"><UButton size="xs" variant="soft" label="Данные" @click="openCargo(shipment)" /></td><td class="p-3"><UButton size="xs" variant="soft" label="Данные" @click="openTransport(shipment)" /></td><td class="p-3"><UButton v-if="shipment.client_company_id === myCompanyId" size="xs" variant="soft" :label="shipment.deal_id ? `Заказ #${shipment.deal_id}` : 'Привязать'" @click="linkDeal(shipment)" /></td></tr>
					<tr v-if="!shipments.length"><td colspan="7" class="p-5 text-gray-500">Перевозок пока нет.</td></tr></tbody></table>
		</div>
		<UModal v-model:open="cargoOpen"><template #content><UCard><template #header><span class="font-medium">Данные о грузе</span></template><div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[65vh] overflow-y-auto"><UFormField v-for="field in cargoFields" :key="field.key" :label="field.label"><UInput v-model="cargo[field.key]" :type="field.type || 'text'" :disabled="!isClient" /></UFormField></div><div v-if="isClient" class="mt-4"><UButton label="Сохранить" @click="saveCargo" /></div></UCard></template></UModal>
		<UModal v-model:open="transportOpen"><template #content><UCard><template #header><span class="font-medium">Данные транспорта</span></template><div v-if="isClient"><p>Транспорт назначается перевозчиком.</p><pre class="text-xs mt-3">{{ selected?.transport_snapshot }}</pre></div><div v-else class="space-y-3"><UFormField label="Транспорт"><USelect v-model="transport.vehicle_id" :items="vehicles.map(v => ({ label: `${v.name} ${v.plate_number || ''}`, value: v.id }))" /></UFormField><UFormField label="Водитель"><USelect v-model="transport.driver_id" :items="drivers.map(d => ({ label: d.full_name, value: d.id }))" /></UFormField><UButton label="Сохранить" @click="saveTransport" /></div></UCard></template></UModal>
	</div>
</template>
