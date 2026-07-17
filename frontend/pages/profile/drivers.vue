<script setup lang="ts">
import type { CompanyDriver } from '~/types/fleet'
import { useFleetApi } from '~/api/me/fleet'

definePageMeta({
	layout: 'profile',
	title: 'Водители',
})

const emptyDraft = () => ({
	full_name: '',
	phone: '',
	license_number: '',
	notes: '',
})

const { listDrivers, createDriver, updateDriver, deleteDriver } = useFleetApi()
const toast = useToast()
const items = ref<CompanyDriver[]>([])
const loading = ref(false)
const editingId = ref<number | null>(null)
const draft = ref(emptyDraft())

const isEditing = computed(() => editingId.value != null)
const formTitle = computed(() => (isEditing.value ? 'Редактировать водителя' : 'Добавить водителя'))
const submitLabel = computed(() => (isEditing.value ? 'Сохранить' : 'Добавить'))

const load = async () => {
	loading.value = true
	try {
		items.value = await listDrivers()
	} catch (e: any) {
		toast.add({ title: 'Ошибка загрузки водителей', description: e?.message, color: 'error' })
	} finally {
		loading.value = false
	}
}

onMounted(load)

const resetForm = () => {
	editingId.value = null
	draft.value = emptyDraft()
}

const startEdit = (row: CompanyDriver) => {
	editingId.value = row.id
	draft.value = {
		full_name: row.full_name || '',
		phone: row.phone || '',
		license_number: row.license_number || '',
		notes: row.notes || '',
	}
}

const submit = async () => {
	if (!draft.value.full_name.trim()) {
		toast.add({ title: 'Укажите ФИО водителя', color: 'warning' })
		return
	}
	const payload = {
		full_name: draft.value.full_name.trim(),
		phone: draft.value.phone.trim() || null,
		license_number: draft.value.license_number.trim() || null,
		notes: draft.value.notes.trim() || null,
	}
	loading.value = true
	try {
		if (editingId.value != null) {
			await updateDriver(editingId.value, payload)
			toast.add({ title: 'Водитель сохранён', color: 'success' })
		} else {
			await createDriver({ ...payload, is_active: true })
			toast.add({ title: 'Водитель добавлен', color: 'success' })
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

const toggleActive = async (row: CompanyDriver) => {
	await updateDriver(row.id, { is_active: !row.is_active })
	await load()
}

const remove = async (id: number) => {
	await deleteDriver(id)
	if (editingId.value === id) resetForm()
	await load()
	toast.add({ title: 'Водитель удалён', color: 'success' })
}
</script>

<template>
	<div class="space-y-6">
		<div>
			<h1 class="text-xl font-semibold text-gray-900">Водители</h1>
			<p class="text-sm text-gray-500 mt-1">Список водителей вашей компании.</p>
		</div>

		<UCard>
			<template #header>
				<span class="font-medium">{{ formTitle }}</span>
			</template>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<UFormField label="ФИО">
					<UInput v-model="draft.full_name" placeholder="Иванов Иван Иванович" />
				</UFormField>
				<UFormField label="Телефон">
					<UInput v-model="draft.phone" placeholder="+7…" />
				</UFormField>
				<UFormField label="ВУ / номер удостоверения">
					<UInput v-model="draft.license_number" />
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
					<p class="font-medium">{{ row.full_name }}</p>
					<p class="text-sm text-gray-500">
						<span v-if="row.phone">{{ row.phone }}</span>
						<span v-if="row.license_number"> · ВУ {{ row.license_number }}</span>
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
		<p v-else class="text-sm text-gray-500">Пока нет водителей — добавьте первого.</p>
	</div>
</template>
