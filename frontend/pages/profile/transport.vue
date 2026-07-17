<script setup lang="ts">
import type { CompanyVehicle } from '~/types/fleet'
import { useFleetApi } from '~/api/me/fleet'

definePageMeta({
	layout: 'profile',
	title: 'Транспорт',
})

const emptyDraft = () => ({
	name: '',
	plate_number: '',
	vehicle_type: '',
	capacity_tons: null as number | null,
	volume_m3: null as number | null,
	notes: '',
})

const { listVehicles, createVehicle, updateVehicle, deleteVehicle } = useFleetApi()
const toast = useToast()
const items = ref<CompanyVehicle[]>([])
const loading = ref(false)
const editingId = ref<number | null>(null)
const draft = ref(emptyDraft())

const isEditing = computed(() => editingId.value != null)
const formTitle = computed(() => (isEditing.value ? 'Редактировать ТС' : 'Добавить ТС'))
const submitLabel = computed(() => (isEditing.value ? 'Сохранить' : 'Добавить'))

const load = async () => {
	loading.value = true
	try {
		items.value = await listVehicles()
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
				<UFormField label="Название / марка">
					<UInput v-model="draft.name" placeholder="Газель Next" />
				</UFormField>
				<UFormField label="Госномер">
					<UInput v-model="draft.plate_number" placeholder="А123ВС 77" />
				</UFormField>
				<UFormField label="Тип">
					<UInput v-model="draft.vehicle_type" placeholder="Тент / рефрижератор…" />
				</UFormField>
				<UFormField label="Грузоподъёмность, т">
					<UInput v-model.number="draft.capacity_tons" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Объём, м³">
					<UInput v-model.number="draft.volume_m3" type="number" step="0.1" />
				</UFormField>
				<UFormField label="Комментарий">
					<UInput v-model="draft.notes" />
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
						<span v-if="row.vehicle_type">{{ row.vehicle_type }}</span>
						<span v-if="row.capacity_tons != null"> · {{ row.capacity_tons }} т</span>
						<span v-if="row.volume_m3 != null"> · {{ row.volume_m3 }} м³</span>
						<span :class="row.is_active ? 'text-green-600' : 'text-gray-400'">
							· {{ row.is_active ? 'активен' : 'неактивен' }}
						</span>
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
