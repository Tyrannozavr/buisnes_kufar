<script setup lang="ts">
import type { CompanyVehicle } from '~/types/fleet'
import { useFleetApi } from '~/api/me/fleet'

definePageMeta({
	layout: 'profile',
	title: 'Транспорт',
})

import type { TransportDictionaries } from '~/types/transport'

const emptyDraft = () => ({
	name: '',
	plate_number: '',
	trailer_plate_number: '',
	trailer_length_m: null as number | null,
	trailer_width_m: null as number | null,
	trailer_height_m: null as number | null,
	load_date: '',
	body_type: '',
	loading_methods: [] as string[],
	adr_classes: [] as string[],
	from_locations_text: '',
	to_locations_text: '',
	partial_load: false,
	partial_load_weight_kg: null as number | null,
	partial_load_volume_m3: null as number | null,
	vehicle_type: '',
	capacity_tons: null as number | null,
	volume_m3: null as number | null,
	notes: '',
})

const { listVehicles, createVehicle, updateVehicle, deleteVehicle } = useFleetApi()
const toast = useToast()
const items = ref<CompanyVehicle[]>([])
const dictionaries = ref<TransportDictionaries>({ body_types: [], loading_methods: [], adr_classes: [] })
const loading = ref(false)
const editingId = ref<number | null>(null)
const draft = ref(emptyDraft())

const isEditing = computed(() => editingId.value != null)
const formTitle = computed(() => (isEditing.value ? 'Редактировать ТС' : 'Добавить ТС'))
const submitLabel = computed(() => (isEditing.value ? 'Сохранить' : 'Добавить'))

const load = async () => {
	loading.value = true
	try {
		const { $api } = useNuxtApp()
		const [vehicles, dicts] = await Promise.all([
			listVehicles(),
			$api.get('/v1/company/fleet-dictionaries') as Promise<TransportDictionaries>,
		])
		items.value = vehicles
		dictionaries.value = dicts
	} catch (e: any) {
		toast.add({ title: 'Ошибка загрузки транспорта', description: e?.message, color: 'error' })
	} finally {
		loading.value = false
	}
}

onMounted(load)

const resetForm = () => {
	editingId.value = null
	draft.value = emptyDraft()
}

const startEdit = (row: CompanyVehicle) => {
	editingId.value = row.id
	draft.value = {
		name: row.name || '',
		plate_number: row.plate_number || '',
		trailer_plate_number: row.trailer_plate_number || '',
		trailer_length_m: row.trailer_length_m ?? null,
		trailer_width_m: row.trailer_width_m ?? null,
		trailer_height_m: row.trailer_height_m ?? null,
		load_date: row.load_date || '',
		body_type: row.body_type || '',
		loading_methods: [...(row.loading_methods || [])],
		adr_classes: [...(row.adr_classes || [])],
		from_locations_text: (row.from_locations || []).map(location => location.name).join(', '),
		to_locations_text: (row.to_locations || []).map(location => location.name).join(', '),
		partial_load: row.partial_load || false,
		partial_load_weight_kg: row.partial_load_weight_kg ?? null,
		partial_load_volume_m3: row.partial_load_volume_m3 ?? null,
		vehicle_type: row.vehicle_type || '',
		capacity_tons: row.capacity_tons ?? null,
		volume_m3: row.volume_m3 ?? null,
		notes: row.notes || '',
	}
}

const submit = async () => {
	if (!draft.value.name.trim()) {
		toast.add({ title: 'Укажите название ТС', color: 'warning' })
		return
	}
	const payload = {
		name: draft.value.name.trim(),
		plate_number: draft.value.plate_number.trim() || null,
		trailer_plate_number: draft.value.trailer_plate_number.trim() || null,
		trailer_length_m: draft.value.trailer_length_m,
		trailer_width_m: draft.value.trailer_width_m,
		trailer_height_m: draft.value.trailer_height_m,
		load_date: draft.value.load_date || null,
		body_type: draft.value.body_type || null,
		loading_methods: draft.value.loading_methods,
		adr_classes: draft.value.adr_classes,
		from_locations: draft.value.from_locations_text.split(',').map(name => name.trim()).filter(Boolean).map(name => ({ name })),
		to_locations: draft.value.to_locations_text.split(',').map(name => name.trim()).filter(Boolean).map(name => ({ name })),
		partial_load: draft.value.partial_load,
		partial_load_weight_kg: draft.value.partial_load ? draft.value.partial_load_weight_kg : null,
		partial_load_volume_m3: draft.value.partial_load ? draft.value.partial_load_volume_m3 : null,
		vehicle_type: draft.value.vehicle_type.trim() || null,
		capacity_tons: draft.value.capacity_tons,
		volume_m3: draft.value.volume_m3,
		notes: draft.value.notes.trim() || null,
	}
	loading.value = true
	try {
		if (editingId.value != null) {
			await updateVehicle(editingId.value, payload)
			toast.add({ title: 'ТС сохранено', color: 'success' })
		} else {
			await createVehicle({ ...payload, is_active: true })
			toast.add({ title: 'ТС добавлено', color: 'success' })
		}
		resetForm()
		await load()
	} catch (e: any) {
		toast.add({
			title: isEditing.value ? 'Не удалось сохранить' : 'Не удалось добавить',
			description: e?.data?.detail || e?.message,
			color: 'error',
		})
	} finally {
		loading.value = false
	}
}

const toggleActive = async (row: CompanyVehicle) => {
	await updateVehicle(row.id, { is_active: !row.is_active })
	await load()
}

const remove = async (id: number) => {
	if (!window.confirm('Удалить транспортное средство?')) return
	await deleteVehicle(id)
	if (editingId.value === id) resetForm()
	await load()
	toast.add({ title: 'ТС удалено', color: 'success' })
}
</script>

<template>
	<div class="space-y-6">
		<div>
			<h1 class="text-xl font-semibold text-gray-900">Транспорт</h1>
			<p class="text-sm text-gray-500 mt-1">Парк транспортных средств вашей компании.</p>
		</div>

		<UCard>
			<template #header>
				<span class="font-medium">{{ formTitle }}</span>
			</template>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<UFormField
					label="Откуда"
					help="Выберите город для точного адреса погрузки (например, Москва) или один/несколько регионов для всех городов этих регионов."
				>
					<UInput v-model="draft.from_locations_text" placeholder="Города или регионы через запятую" />
				</UFormField>
				<UFormField
					label="Куда"
					help="Город, регион(ы) или страна для доставки в любой город страны (например, Россия)."
				>
					<UInput v-model="draft.to_locations_text" placeholder="Города или регионы через запятую" />
				</UFormField>
				<UFormField label="Название / марка">
					<UInput v-model="draft.name" placeholder="Газель Next" />
				</UFormField>
				<UFormField label="Госномер">
					<UInput v-model="draft.plate_number" placeholder="А123ВС 77" />
				</UFormField>
				<UFormField label="Тип кузова">
					<USelect v-model="draft.body_type" :items="dictionaries.body_types" placeholder="Выберите тип" />
				</UFormField>
				<UFormField label="Грузоподъёмность, т">
					<UInput v-model.number="draft.capacity_tons" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Объём, м³">
					<UInput v-model.number="draft.volume_m3" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Номер прицепа">
					<UInput v-model="draft.trailer_plate_number" />
				</UFormField>
				<UFormField label="Дата загрузки">
					<UInput v-model="draft.load_date" type="date" />
				</UFormField>
				<UFormField label="Длина прицепа, м">
					<UInput v-model.number="draft.trailer_length_m" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Ширина прицепа, м">
					<UInput v-model.number="draft.trailer_width_m" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Высота прицепа, м">
					<UInput v-model.number="draft.trailer_height_m" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Способы загрузки">
					<USelectMenu v-model="draft.loading_methods" :items="dictionaries.loading_methods" multiple />
				</UFormField>
				<UFormField label="Классы ADR">
					<USelectMenu v-model="draft.adr_classes" :items="dictionaries.adr_classes" multiple />
				</UFormField>
				<UFormField label="Комментарий">
					<UInput v-model="draft.notes" />
				</UFormField>
			</div>
			<div class="mt-3 flex items-center gap-2">
				<UCheckbox v-model="draft.partial_load" label="Готов к догрузу" />
			</div>
			<div v-if="draft.partial_load" class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
				<UFormField label="Догруз, кг">
					<UInput v-model.number="draft.partial_load_weight_kg" type="number" />
				</UFormField>
				<UFormField label="Догруз, м³">
					<UInput v-model.number="draft.partial_load_volume_m3" type="number" step="0.1" />
				</UFormField>
			</div>
			<div class="mt-4 flex flex-wrap gap-2">
				<UButton :label="submitLabel" color="primary" :loading="loading" @click="submit" />
				<UButton
					v-if="isEditing"
					label="Отмена"
					color="neutral"
					variant="soft"
					:disabled="loading"
					@click="resetForm"
				/>
			</div>
		</UCard>

		<ul v-if="items.length" class="space-y-2">
			<li
				v-for="row in items"
				:key="row.id"
				class="border border-gray-200 rounded-lg p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
				:class="editingId === row.id ? 'border-primary-300 bg-primary-50/40' : ''"
			>
				<div>
					<p class="font-medium">
						{{ row.name }}
						<span v-if="row.plate_number" class="text-gray-500 font-normal"> · {{ row.plate_number }}</span>
					</p>
					<p class="text-sm text-gray-500">
						<span v-if="row.body_type">{{ row.body_type }}</span>
						<span v-if="row.capacity_tons != null"> · {{ row.capacity_tons }} т</span>
						<span v-if="row.volume_m3 != null"> · {{ row.volume_m3 }} м³</span>
						<span :class="row.is_active ? 'text-green-600' : 'text-gray-400'">
							· {{ row.is_active ? 'активен' : 'неактивен' }}
						</span>
					</p>
					<p class="text-sm text-gray-500">
						{{ row.from_locations?.map(location => location.name).join(', ') || '—' }}
						→ {{ row.to_locations?.map(location => location.name).join(', ') || '—' }}
						<span v-if="row.partial_load"> · догруз {{ row.partial_load_weight_kg || '—' }} кг</span>
					</p>
				</div>
				<div class="flex flex-wrap gap-2">
					<UButton size="sm" color="primary" variant="soft" label="Редактировать" @click="startEdit(row)" />
					<UButton size="sm" color="neutral" variant="soft" :label="row.is_active ? 'Выключить' : 'Включить'" @click="toggleActive(row)" />
					<UButton size="sm" color="error" variant="ghost" label="Удалить" @click="remove(row.id)" />
				</div>
			</li>
		</ul>
		<p v-else class="text-sm text-gray-500">Пока нет транспорта — добавьте первое ТС.</p>
	</div>
</template>
