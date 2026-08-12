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
const formOpen = ref(false)
const viewOpen = ref(false)
const viewing = ref<CompanyVehicle | null>(null)
const editingId = ref<number | null>(null)
const draft = ref(emptyDraft())

const isEditing = computed(() => editingId.value != null)
const formTitle = computed(() => (isEditing.value ? 'Редактировать ТС' : 'Добавить ТС'))
const submitLabel = computed(() => (isEditing.value ? 'Сохранить' : 'Добавить'))

const loc = (items?: { name?: string }[]) => (items || []).map(x => x.name).filter(Boolean).join(', ') || '—'

const formatDate = (value?: string | null) => {
	if (!value) return '—'
	const d = new Date(value)
	return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString('ru-RU')
}

const trailerSize = (row: CompanyVehicle) => {
	const parts = [row.trailer_length_m, row.trailer_width_m, row.trailer_height_m]
		.filter((v): v is number => v != null)
	if (!parts.length) return '—'
	return `${parts.join('×')} м (Д×Ш×В)`
}

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
		if (viewing.value) {
			viewing.value = vehicles.find(v => v.id === viewing.value!.id) || null
			if (!viewing.value) viewOpen.value = false
		}
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

const closeForm = () => {
	formOpen.value = false
	resetForm()
}

const openCreate = () => {
	resetForm()
	formOpen.value = true
}

const openView = (row: CompanyVehicle) => {
	viewing.value = row
	viewOpen.value = true
}

const fillDraftFromRow = (row: CompanyVehicle) => {
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

const startEditFromView = () => {
	if (!viewing.value) return
	fillDraftFromRow(viewing.value)
	viewOpen.value = false
	formOpen.value = true
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
		closeForm()
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

const setActive = async (row: CompanyVehicle, isActive: boolean) => {
	if (row.is_active === isActive) return
	await updateVehicle(row.id, { is_active: isActive })
	await load()
}

const {
	deleteOpen,
	deleteLoading,
	deleteTitle,
	deleteMessage,
	askDelete,
	confirmDelete,
} = useConfirmDelete()

const remove = (id: number) => {
	const row = items.value.find(v => v.id === id)
	askDelete({
		message: row
			? `Точно хотите удалить ТС «${row.name}»${row.plate_number ? ` · ${row.plate_number}` : ''}?\nЭто действие нельзя отменить.`
			: 'Точно хотите удалить транспортное средство?\nЭто действие нельзя отменить.',
		onConfirm: async () => {
			await deleteVehicle(id)
			if (editingId.value === id) closeForm()
			if (viewing.value?.id === id) {
				viewOpen.value = false
				viewing.value = null
			}
			await load()
			toast.add({ title: 'ТС удалено', color: 'success' })
		},
	})
}
</script>

<template>
	<div class="space-y-6">
		<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-xl font-semibold text-gray-900">Транспорт</h1>
				<p class="text-sm text-gray-500 mt-1">Парк транспортных средств вашей компании.</p>
			</div>
			<UButton
				color="primary"
				icon="i-lucide-plus"
				label="Добавить ТС"
				@click="openCreate"
			/>
		</div>

		<ul v-if="items.length" class="space-y-2">
			<li
				v-for="row in items"
				:key="row.id"
				class="border border-gray-200 rounded-lg p-3 flex items-center justify-between gap-3 hover:border-primary-300 hover:bg-primary-50/30 transition-colors"
			>
				<div
					class="min-w-0 flex-1 cursor-pointer"
					role="button"
					tabindex="0"
					@click="openView(row)"
					@keydown.enter.prevent="openView(row)"
				>
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
						{{ loc(row.from_locations) }} → {{ loc(row.to_locations) }}
						<span v-if="row.partial_load"> · догруз {{ row.partial_load_weight_kg || '—' }} кг</span>
					</p>
					<p v-if="row.notes" class="text-sm text-gray-500 truncate">
						{{ row.notes }}
					</p>
				</div>
				<div class="flex flex-col items-center gap-2 shrink-0 relative z-10">
					<USwitch
						:model-value="row.is_active"
						color="success"
						size="md"
						:aria-label="row.is_active ? 'Выключить ТС' : 'Включить ТС'"
						@update:model-value="(v: boolean) => setActive(row, v)"
					/>
					<UButton
						size="sm"
						color="error"
						variant="outline"
						label="Удалить"
						class="cursor-pointer"
						@click.stop.prevent="remove(row.id)"
					/>
				</div>
			</li>
		</ul>
		<p v-else class="text-sm text-gray-500">Пока нет транспорта — добавьте первое ТС.</p>

		<UModal
			v-model:open="viewOpen"
			:title="viewing ? `${viewing.name}${viewing.plate_number ? ` · ${viewing.plate_number}` : ''}` : 'ТС'"
			@update:open="(open) => { if (!open) viewing = null }"
		>
			<template #body>
				<div v-if="viewing" class="space-y-4 p-1 sm:p-2">
					<div class="flex flex-wrap justify-between gap-2">
						<UButton
							color="primary"
							icon="i-lucide-pencil"
							label="Редактировать"
							@click="startEditFromView"
						/>
						<span
							class="self-center text-sm"
							:class="viewing.is_active ? 'text-green-600' : 'text-gray-400'"
						>
							{{ viewing.is_active ? 'активен' : 'неактивен' }}
						</span>
					</div>
					<dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3 text-sm">
						<div>
							<dt class="text-gray-500">Откуда</dt>
							<dd class="font-medium text-gray-900">{{ loc(viewing.from_locations) }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Куда</dt>
							<dd class="font-medium text-gray-900">{{ loc(viewing.to_locations) }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Тип кузова</dt>
							<dd class="font-medium text-gray-900">{{ viewing.body_type || '—' }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Грузоподъёмность</dt>
							<dd class="font-medium text-gray-900">{{ viewing.capacity_tons != null ? `${viewing.capacity_tons} т` : '—' }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Объём</dt>
							<dd class="font-medium text-gray-900">{{ viewing.volume_m3 != null ? `${viewing.volume_m3} м³` : '—' }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Номер прицепа</dt>
							<dd class="font-medium text-gray-900">{{ viewing.trailer_plate_number || '—' }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Дата загрузки</dt>
							<dd class="font-medium text-gray-900">{{ formatDate(viewing.load_date) }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">Габариты п/п</dt>
							<dd class="font-medium text-gray-900">{{ trailerSize(viewing) }}</dd>
						</div>
						<div class="sm:col-span-2">
							<dt class="text-gray-500">Способы загрузки</dt>
							<dd class="font-medium text-gray-900">{{ viewing.loading_methods?.length ? viewing.loading_methods.join(', ') : '—' }}</dd>
						</div>
						<div class="sm:col-span-2">
							<dt class="text-gray-500">Классы ADR</dt>
							<dd class="font-medium text-gray-900">{{ viewing.adr_classes?.length ? viewing.adr_classes.join(', ') : '—' }}</dd>
						</div>
						<div class="sm:col-span-2">
							<dt class="text-gray-500">Догруз</dt>
							<dd class="font-medium text-gray-900">
								<template v-if="viewing.partial_load">
									да
									<span v-if="viewing.partial_load_weight_kg != null"> · {{ viewing.partial_load_weight_kg }} кг</span>
									<span v-if="viewing.partial_load_volume_m3 != null"> · {{ viewing.partial_load_volume_m3 }} м³</span>
								</template>
								<template v-else>нет</template>
							</dd>
						</div>
						<div v-if="viewing.notes" class="sm:col-span-2">
							<dt class="text-gray-500">Комментарий</dt>
							<dd class="font-medium text-gray-900">{{ viewing.notes }}</dd>
						</div>
					</dl>
				</div>
			</template>
		</UModal>

		<UModal v-model:open="formOpen" :title="formTitle" @update:open="(open) => { if (!open) resetForm() }">
			<template #body>
				<div class="space-y-4 p-1 sm:p-2 max-h-[70vh] overflow-y-auto">
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<UFormField>
							<template #label>
								<span class="inline-flex items-center gap-1">
									Откуда
									<UTooltip text="Город для точного адреса или регион(ы) через запятую.">
										<UIcon
											name="i-heroicons-question-mark-circle"
											class="size-4 text-gray-400 cursor-help shrink-0"
										/>
									</UTooltip>
								</span>
							</template>
							<UInput v-model="draft.from_locations_text" placeholder="Города или регионы через запятую" />
						</UFormField>
						<UFormField>
							<template #label>
								<span class="inline-flex items-center gap-1">
									Куда
									<UTooltip text="Город, регион(ы) или страна.">
										<UIcon
											name="i-heroicons-question-mark-circle"
											class="size-4 text-gray-400 cursor-help shrink-0"
										/>
									</UTooltip>
								</span>
							</template>
							<UInput v-model="draft.to_locations_text" placeholder="Города или регионы через запятую" />
						</UFormField>
						<UFormField label="Название / марка">
							<UInput v-model="draft.name" placeholder="Газель Next" />
						</UFormField>
						<UFormField label="Госномер">
							<UInput v-model="draft.plate_number" placeholder="А123ВС 77" />
						</UFormField>
						<UFormField label="Тип кузова">
							<USelect
								v-model="draft.body_type"
								:items="dictionaries.body_types"
								placeholder="Выберите тип"
								class="w-full"
							/>
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
						<UFormField label="Способы загрузки" class="sm:col-span-2">
							<USelectMenu
								v-model="draft.loading_methods"
								:items="dictionaries.loading_methods"
								multiple
								placeholder="Выберите способы"
							/>
						</UFormField>
						<UFormField label="Классы ADR" class="sm:col-span-2">
							<USelectMenu
								v-model="draft.adr_classes"
								:items="dictionaries.adr_classes"
								multiple
								placeholder="Выберите классы"
							/>
						</UFormField>
						<UFormField label="Комментарий" class="sm:col-span-2">
							<UInput v-model="draft.notes" />
						</UFormField>
					</div>
					<div class="flex items-center gap-2">
						<UCheckbox v-model="draft.partial_load" label="Готов к догрузу" />
					</div>
					<div v-if="draft.partial_load" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<UFormField label="Догруз, кг">
							<UInput v-model.number="draft.partial_load_weight_kg" type="number" />
						</UFormField>
						<UFormField label="Догруз, м³">
							<UInput v-model.number="draft.partial_load_volume_m3" type="number" step="0.1" />
						</UFormField>
					</div>
					<div class="flex flex-wrap justify-end gap-2 pt-2">
						<UButton
							label="Отмена"
							color="neutral"
							variant="outline"
							:disabled="loading"
							@click="closeForm"
						/>
						<UButton :label="submitLabel" color="primary" :loading="loading" @click="submit" />
					</div>
				</div>
			</template>
		</UModal>

		<ConfirmDeleteModal
			v-model:open="deleteOpen"
			:title="deleteTitle"
			:message="deleteMessage"
			:loading="deleteLoading"
			@confirm="confirmDelete"
		/>
	</div>
</template>
