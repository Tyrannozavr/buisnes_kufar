<script setup lang="ts">
import type { CargoData, Shipment, ShipmentCompanyBrief, TransportDetail } from '~/types/transport'
import type { CompanyDriver, CompanyVehicle } from '~/types/fleet'
import type { SellerDealResponse } from '~/types/dealResponse'
import { useTransportApi } from '~/api/transport'
import { useFleetApi } from '~/api/me/fleet'
import { usePurchasesApi } from '~/api/purchases'

definePageMeta({
	layout: 'profile',
	title: 'Перевозки',
})

type TransportSnapshot = {
	vehicle?: {
		id?: number
		name?: string | null
		plate_number?: string | null
		trailer_plate_number?: string | null
	} | null
	driver?: {
		id?: number
		full_name?: string | null
		phone?: string | null
		license_number?: string | null
	} | null
}

const { $api } = useNuxtApp()
const {
	listShipments,
	getCargo,
	getTransport,
	updateCargo,
	updateTransport,
	updateDeal,
} = useTransportApi()
const { listVehicles, listDrivers } = useFleetApi()
const { getSellerDeals } = usePurchasesApi()
const toast = useToast()
const myCompanyId = ref<number | null>(null)
const shipments = ref<Shipment[]>([])
const vehicles = ref<CompanyVehicle[]>([])
const drivers = ref<CompanyDriver[]>([])
const fleetLoaded = ref(false)
const selected = ref<Shipment | null>(null)
const detailOpen = ref(false)
const cargoOpen = ref(false)
const transportOpen = ref(false)
const dealOpen = ref(false)
const dealSaving = ref(false)
const dealLoading = ref(false)
const dealId = ref<number | null>(null)
const sellerDeals = ref<SellerDealResponse[]>([])
const cargo = ref<CargoData>({})
const cargoLoading = ref(false)
const transportLoading = ref(false)
const detailLoading = ref(false)
const transport = ref({ vehicle_id: null as number | null, driver_id: null as number | null })
const transportDetail = ref<TransportDetail | null>(null)
const cargoFields: { key: keyof CargoData, label: string, type?: string, step?: string, placeholder?: string }[] = [
	{ key: 'loading_date', label: 'Дата загрузки', type: 'date' },
	{ key: 'loading_time', label: 'Время загрузки', type: 'time', step: '60', placeholder: 'HH:MM' },
	{ key: 'loading_address', label: 'Адрес загрузки' },
	{ key: 'unloading_date', label: 'Дата выгрузки', type: 'date' },
	{ key: 'unloading_time', label: 'Время выгрузки', type: 'time', step: '60', placeholder: 'HH:MM' },
	{ key: 'unloading_address', label: 'Адрес выгрузки' },
	{ key: 'route', label: 'Маршрут' }, { key: 'cargo_name', label: 'Наименование груза' }, { key: 'transport_conditions', label: 'Условия перевозки' },
	{ key: 'net_weight', label: 'Вес нетто, кг', type: 'number' }, { key: 'gross_weight', label: 'Вес брутто, кг', type: 'number' }, { key: 'places_count', label: 'Количество мест', type: 'number' },
	{ key: 'volume', label: 'Объём, м³', type: 'number' }, { key: 'marking', label: 'Маркировка' }, { key: 'packaging_type', label: 'Тип упаковки' },
	{ key: 'packaging', label: 'Упаковка' }, { key: 'seal', label: 'Пломба' }, { key: 'rate', label: 'Ставка', type: 'number' },
	{ key: 'payment_terms', label: 'Условия оплаты' }, { key: 'declared_value', label: 'Объявленная ценность', type: 'number' }, { key: 'identity_document_requisites', label: 'Реквизиты документа' },
]
const isClient = computed(() => selected.value != null && selected.value.client_company_id === myCompanyId.value)

const transportSnapshot = computed(() => (transportDetail.value?.transport_snapshot || {}) as TransportSnapshot)
const hasTransportAssigned = computed(() => {
	const snap = transportSnapshot.value
	return !!(snap.vehicle?.id || snap.driver?.id || snap.vehicle?.plate_number || snap.driver?.full_name)
})

const cargoSummary = computed(() => {
	const name = cargo.value.cargo_name?.trim()
	const route = cargo.value.route?.trim()
	if (name && route) return `${name} · ${route}`
	if (name) return name
	if (route) return route
	const filled = Object.values(cargo.value).some(v => v != null && v !== '')
	return filled ? 'Данные заполнены' : 'Пока пусто'
})

const transportSummary = computed(() => {
	if (!hasTransportAssigned.value) return 'Ещё не назначен'
	const vehicle = transportSnapshot.value.vehicle
	const driver = transportSnapshot.value.driver
	const parts = [
		vehicle?.name || vehicle?.plate_number,
		driver?.full_name,
	].filter(Boolean)
	return parts.join(' · ') || 'Назначен'
})

const usedDealIds = computed(() => {
	const currentId = selected.value?.id
	return new Set(
		shipments.value
			.filter(s => s.deal_id != null && s.id !== currentId)
			.map(s => Number(s.deal_id)),
	)
})

const dealItems = computed(() =>
	sellerDeals.value
		.filter(d => d.status === 'Активная' && (!usedDealIds.value.has(d.id) || d.id === dealId.value))
		.map(d => ({
			label: [
				`№ ${d.seller_order_number || d.id}`,
				d.buyer_name,
				d.total_amount != null ? `${Number(d.total_amount).toLocaleString('ru-RU')} BYN` : null,
			].filter(Boolean).join(' · '),
			value: d.id,
		})),
)

const sameCompany = (a?: number | null, b?: number | null) =>
	a != null && b != null && Number(a) === Number(b)

/** Для перевозчика — клиент; для клиента — перевозчик. */
const counterparty = (shipment: Shipment): ShipmentCompanyBrief | null => {
	if (sameCompany(shipment.client_company_id, myCompanyId.value)) {
		return shipment.carrier_company || null
	}
	return shipment.client_company || null
}

const companyTitle = (company: ShipmentCompanyBrief) => {
	const type = company.type?.trim()
	const name = company.name?.trim() || `Компания #${company.id}`
	if (type && !name.startsWith(type)) return `${type} «${name}»`
	return name
}

const formatDate = (value: string) => new Date(value).toLocaleDateString('ru-RU')

/** Нормализация к HH:MM для input[type=time]. */
const toTimeInputValue = (value?: string | null) => {
	if (!value) return ''
	const match = String(value).trim().match(/^(\d{1,2}):(\d{2})/)
	if (!match) return ''
	return `${match[1].padStart(2, '0')}:${match[2]}`
}

const normalizeCargoTimes = (data: CargoData): CargoData => ({
	...data,
	loading_time: toTimeInputValue(data.loading_time) || null,
	unloading_time: toTimeInputValue(data.unloading_time) || null,
})

const applyCargoDetail = (data: CargoData) => {
	cargo.value = normalizeCargoTimes({ ...(data || {}) })
}

const applyTransportDetail = (detail: TransportDetail) => {
	transportDetail.value = detail
	transport.value = {
		vehicle_id: detail.vehicle_id || null,
		driver_id: detail.driver_id || null,
	}
}

const ensureFleet = async () => {
	if (fleetLoaded.value) return
	;[vehicles.value, drivers.value] = await Promise.all([listVehicles(), listDrivers()])
	fleetLoaded.value = true
}

const fetchCargo = async (shipmentId: number) => {
	cargoLoading.value = true
	try {
		const detail = await getCargo(shipmentId)
		applyCargoDetail(detail.cargo_data)
	} finally {
		cargoLoading.value = false
	}
}

const fetchTransport = async (shipmentId: number) => {
	transportLoading.value = true
	try {
		const detail = await getTransport(shipmentId)
		applyTransportDetail(detail)
	} finally {
		transportLoading.value = false
	}
}

const load = async () => {
	try {
		const company = await $api.get('/v1/company/me') as { id: number }
		myCompanyId.value = Number(company.id)
		shipments.value = await listShipments()
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить перевозки', description: e?.message, color: 'error' })
	}
}
onMounted(load)

/** Мобилка: клик по строке → сразу GET cargo + GET transport. */
const openDetails = async (shipment: Shipment) => {
	selected.value = shipment
	cargo.value = {}
	transportDetail.value = null
	detailOpen.value = true
	detailLoading.value = true
	try {
		await Promise.all([fetchCargo(shipment.id), fetchTransport(shipment.id)])
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить данные перевозки', description: e?.message, color: 'error' })
	} finally {
		detailLoading.value = false
	}
}

const openCargo = async (shipment: Shipment) => {
	selected.value = shipment
	detailOpen.value = false
	cargoOpen.value = true
	try {
		await fetchCargo(shipment.id)
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить груз', description: e?.message, color: 'error' })
	}
}

const openTransport = async (shipment: Shipment) => {
	selected.value = shipment
	detailOpen.value = false
	transportOpen.value = true
	try {
		await Promise.all([
			fetchTransport(shipment.id),
			sameCompany(shipment.carrier_company_id, myCompanyId.value) ? ensureFleet() : Promise.resolve(),
		])
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить транспорт', description: e?.message, color: 'error' })
	}
}

const saveCargo = async () => {
	if (selected.value) {
		await updateCargo(selected.value.id, normalizeCargoTimes(cargo.value))
		cargoOpen.value = false
		toast.add({ title: 'Данные груза сохранены', color: 'success' })
	}
}
const saveTransport = async () => {
	if (selected.value) {
		const updated = await updateTransport(selected.value.id, transport.value)
		applyTransportDetail({
			shipment_id: selected.value.id,
			vehicle_id: updated.vehicle_id,
			driver_id: updated.driver_id,
			transport_snapshot: updated.transport_snapshot || {},
		})
		transportOpen.value = false
		toast.add({ title: 'Транспорт назначен', color: 'success' })
	}
}

const openLinkDeal = async (shipment: Shipment) => {
	selected.value = shipment
	dealId.value = shipment.deal_id || null
	detailOpen.value = false
	dealOpen.value = true
	dealLoading.value = true
	try {
		sellerDeals.value = (await getSellerDeals(0, 100)) || []
	} catch (e: any) {
		toast.add({ title: 'Не удалось загрузить заказы', description: e?.message, color: 'error' })
	} finally {
		dealLoading.value = false
	}
}

const saveDeal = async () => {
	if (!selected.value || !dealId.value) {
		toast.add({ title: 'Выберите активный заказ продажи', color: 'warning' })
		return
	}
	dealSaving.value = true
	try {
		await updateDeal(selected.value.id, dealId.value)
		dealOpen.value = false
		await load()
		toast.add({ title: 'Заказ привязан', color: 'success' })
	} catch (e: any) {
		toast.add({
			title: 'Не удалось привязать заказ',
			description: e?.data?.detail || e?.message,
			color: 'error',
		})
	} finally {
		dealSaving.value = false
	}
}
</script>

<template>
	<div class="space-y-5">
		<div>
			<h1 class="text-xl font-semibold">Перевозки</h1>
			<p class="text-sm text-gray-500">Данные груза редактирует клиент, транспорт назначает перевозчик.</p>
		</div>

		<!-- Mobile: карточки, клик → 2 запроса (груз + транспорт) -->
		<ul v-if="shipments.length" class="md:hidden space-y-3">
			<li
				v-for="shipment in shipments"
				:key="shipment.id"
				role="button"
				tabindex="0"
				class="border border-gray-200 rounded-lg p-4 cursor-pointer active:bg-gray-50"
				@click="openDetails(shipment)"
				@keydown.enter.prevent="openDetails(shipment)"
			>
				<div class="flex items-start justify-between gap-3">
					<div class="min-w-0">
						<p class="font-medium text-gray-900">№ {{ shipment.number }}/{{ shipment.year }}</p>
						<p class="mt-0.5 text-sm text-gray-500">{{ formatDate(shipment.created_at) }}</p>
						<p class="mt-2 text-sm text-primary-700 truncate">
							{{ counterparty(shipment) ? companyTitle(counterparty(shipment)!) : '—' }}
						</p>
					</div>
					<UIcon name="i-heroicons-chevron-right" class="size-5 text-gray-400 shrink-0 mt-0.5" />
				</div>
			</li>
		</ul>
		<p v-else class="md:hidden text-sm text-gray-500 py-4">Перевозок пока нет.</p>

		<!-- Desktop: таблица -->
		<div class="hidden md:block overflow-x-auto border rounded-lg">
			<table class="min-w-full text-sm">
				<thead class="bg-gray-50">
					<tr>
						<th class="p-3 text-left">Заказ</th>
						<th class="p-3 text-left">Дата</th>
						<th class="p-3 text-left">Контрагент</th>
						<th class="p-3 text-left">Договор</th>
						<th class="p-3 text-left">Груз</th>
						<th class="p-3 text-left">Транспорт</th>
						<th class="p-3 text-left">К заказу клиента</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="shipment in shipments" :key="shipment.id" class="border-t">
						<td class="p-3">№ {{ shipment.number }}/{{ shipment.year }}</td>
						<td class="p-3">{{ formatDate(shipment.created_at) }}</td>
						<td class="p-3">
							<NuxtLink
								v-if="counterparty(shipment)?.slug"
								:to="`/companies/${counterparty(shipment)!.slug}`"
								class="text-primary-600 hover:underline cursor-pointer"
							>
								{{ companyTitle(counterparty(shipment)!) }}
							</NuxtLink>
							<span v-else-if="counterparty(shipment)">
								{{ companyTitle(counterparty(shipment)!) }}
							</span>
							<span v-else class="text-gray-500">—</span>
						</td>
						<td class="p-3">Позже</td>
						<td class="p-3">
							<UButton size="xs" variant="soft" label="Данные" class="cursor-pointer" @click="openCargo(shipment)" />
						</td>
						<td class="p-3">
							<UButton size="xs" variant="soft" label="Данные" class="cursor-pointer" @click="openTransport(shipment)" />
						</td>
						<td class="p-3">
							<UButton
								v-if="sameCompany(shipment.client_company_id, myCompanyId)"
								size="xs"
								variant="soft"
								:label="shipment.deal_id ? `Заказ #${shipment.deal_id}` : 'Привязать'"
								class="cursor-pointer"
								@click="openLinkDeal(shipment)"
							/>
						</td>
					</tr>
					<tr v-if="!shipments.length">
						<td colspan="7" class="p-5 text-gray-500">Перевозок пока нет.</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Mobile detail -->
		<UModal
			v-model:open="detailOpen"
			:title="selected ? `Перевозка № ${selected.number}/${selected.year}` : 'Перевозка'"
		>
			<template #body>
				<div v-if="selected" class="space-y-4">
					<dl class="space-y-3 text-sm">
						<div class="flex justify-between gap-3">
							<dt class="text-gray-500 shrink-0">Дата</dt>
							<dd class="text-right">{{ formatDate(selected.created_at) }}</dd>
						</div>
						<div class="flex justify-between gap-3 items-start">
							<dt class="text-gray-500 shrink-0">Контрагент</dt>
							<dd class="text-right min-w-0">
								<NuxtLink
									v-if="counterparty(selected)?.slug"
									:to="`/companies/${counterparty(selected)!.slug}`"
									class="text-primary-600 hover:underline cursor-pointer"
									@click="detailOpen = false"
								>
									{{ companyTitle(counterparty(selected)!) }}
								</NuxtLink>
								<span v-else-if="counterparty(selected)">
									{{ companyTitle(counterparty(selected)!) }}
								</span>
								<span v-else>—</span>
							</dd>
						</div>
						<div class="flex justify-between gap-3">
							<dt class="text-gray-500 shrink-0">Договор</dt>
							<dd class="text-right">Позже</dd>
						</div>
						<div class="flex justify-between gap-3">
							<dt class="text-gray-500 shrink-0">К заказу клиента</dt>
							<dd class="text-right">
								{{ selected.deal_id ? `Заказ #${selected.deal_id}` : 'Не привязан' }}
							</dd>
						</div>
						<div class="flex justify-between gap-3 items-start">
							<dt class="text-gray-500 shrink-0">Груз</dt>
							<dd class="text-right text-gray-800">
								<span v-if="detailLoading || cargoLoading">Загрузка…</span>
								<span v-else>{{ cargoSummary }}</span>
							</dd>
						</div>
						<div class="flex justify-between gap-3 items-start">
							<dt class="text-gray-500 shrink-0">Транспорт</dt>
							<dd class="text-right text-gray-800">
								<span v-if="detailLoading || transportLoading">Загрузка…</span>
								<span v-else>{{ transportSummary }}</span>
							</dd>
						</div>
					</dl>

					<div class="flex flex-col gap-2 pt-1">
						<UButton
							label="Данные о грузе"
							variant="soft"
							block
							class="cursor-pointer"
							:disabled="detailLoading"
							@click="openCargo(selected)"
						/>
						<UButton
							label="Данные транспорта"
							variant="soft"
							block
							class="cursor-pointer"
							:disabled="detailLoading"
							@click="openTransport(selected)"
						/>
						<UButton
							v-if="sameCompany(selected.client_company_id, myCompanyId)"
							:label="selected.deal_id ? `Заказ #${selected.deal_id}` : 'Привязать к заказу'"
							color="primary"
							block
							class="cursor-pointer"
							@click="openLinkDeal(selected)"
						/>
					</div>
				</div>
			</template>
			<template #footer>
				<div class="flex justify-end">
					<UButton
						label="Закрыть"
						color="neutral"
						variant="outline"
						class="cursor-pointer"
						@click="detailOpen = false"
					/>
				</div>
			</template>
		</UModal>

		<UModal v-model:open="cargoOpen">
			<template #content>
				<UCard>
					<template #header><span class="font-medium">Данные о грузе</span></template>
					<p v-if="cargoLoading" class="text-sm text-gray-500 mb-3">Загрузка…</p>
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[65vh] overflow-y-auto">
						<UFormField v-for="field in cargoFields" :key="field.key" :label="field.label">
							<UInput
								v-model="cargo[field.key]"
								:type="field.type || 'text'"
								:step="field.step"
								:placeholder="field.placeholder"
								:disabled="!isClient || cargoLoading"
							/>
						</UFormField>
					</div>
					<div v-if="isClient" class="mt-4">
						<UButton label="Сохранить" class="cursor-pointer" :disabled="cargoLoading" @click="saveCargo" />
					</div>
				</UCard>
			</template>
		</UModal>
		<UModal v-model:open="transportOpen">
			<template #content>
				<UCard>
					<template #header><span class="font-medium">Данные транспорта</span></template>
					<p v-if="transportLoading" class="text-sm text-gray-500 mb-3">Загрузка…</p>
					<div v-if="isClient" class="space-y-3 text-sm">
						<p class="text-gray-500">Транспорт назначает перевозчик. Здесь только просмотр.</p>
						<template v-if="!transportLoading && hasTransportAssigned">
							<div class="space-y-2 rounded-lg border border-gray-200 p-3">
								<p v-if="transportSnapshot.vehicle">
									<span class="text-gray-500">Транспорт:</span>
									{{ transportSnapshot.vehicle.name || '—' }}
									<span v-if="transportSnapshot.vehicle.plate_number" class="text-gray-700">
										· {{ transportSnapshot.vehicle.plate_number }}
									</span>
									<span v-if="transportSnapshot.vehicle.trailer_plate_number" class="text-gray-500">
										(прицеп {{ transportSnapshot.vehicle.trailer_plate_number }})
									</span>
								</p>
								<p v-if="transportSnapshot.driver">
									<span class="text-gray-500">Водитель:</span>
									{{ transportSnapshot.driver.full_name || '—' }}
									<span v-if="transportSnapshot.driver.phone" class="text-gray-700">
										· {{ transportSnapshot.driver.phone }}
									</span>
								</p>
							</div>
						</template>
						<p v-else-if="!transportLoading" class="text-gray-600">Перевозчик ещё не назначил транспорт и водителя.</p>
					</div>
					<div v-else class="space-y-3">
						<UFormField label="Транспорт">
							<USelect
								v-model="transport.vehicle_id"
								:items="vehicles.map(v => ({ label: `${v.name} ${v.plate_number || ''}`, value: v.id }))"
								:disabled="transportLoading"
							/>
						</UFormField>
						<UFormField label="Водитель">
							<USelect
								v-model="transport.driver_id"
								:items="drivers.map(d => ({ label: d.full_name, value: d.id }))"
								:disabled="transportLoading"
							/>
						</UFormField>
						<UButton label="Сохранить" class="cursor-pointer" :disabled="transportLoading" @click="saveTransport" />
					</div>
				</UCard>
			</template>
		</UModal>

		<UModal v-model:open="dealOpen">
			<template #content>
				<UCard>
					<template #header><span class="font-medium">К заказу клиента</span></template>
					<p class="text-sm text-gray-500 mb-3">
						Выберите активный заказ из Продаж. Один заказ — одна перевозка.
					</p>
					<p v-if="dealLoading" class="text-sm text-gray-500">Загрузка заказов…</p>
					<template v-else>
						<UFormField label="Активный заказ продажи">
							<USelect
								v-model="dealId"
								:items="dealItems"
								placeholder="Выберите заказ"
								:disabled="!dealItems.length"
							/>
						</UFormField>
						<p v-if="!dealItems.length" class="mt-2 text-sm text-amber-700">
							Нет свободных активных заказов продажи. Создайте или откройте заказ в разделе Продажи.
						</p>
						<div class="mt-4 flex justify-end gap-2">
							<UButton
								label="Отмена"
								color="neutral"
								variant="outline"
								class="cursor-pointer"
								@click="dealOpen = false"
							/>
							<UButton
								label="Привязать"
								class="cursor-pointer"
								:loading="dealSaving"
								:disabled="!dealId || !dealItems.length"
								@click="saveDeal"
							/>
						</div>
					</template>
				</UCard>
			</template>
		</UModal>
	</div>
</template>
