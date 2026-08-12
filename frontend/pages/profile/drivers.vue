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
	inn: '',
	notes: '',
})

const { listDrivers, createDriver, updateDriver, deleteDriver } = useFleetApi()
const toast = useToast()
const items = ref<CompanyDriver[]>([])
const loading = ref(false)
const formOpen = ref(false)
const viewOpen = ref(false)
const viewing = ref<CompanyDriver | null>(null)
const editingId = ref<number | null>(null)
const draft = ref(emptyDraft())

const isEditing = computed(() => editingId.value != null)
const formTitle = computed(() => (isEditing.value ? 'Редактировать водителя' : 'Добавить водителя'))
const submitLabel = computed(() => (isEditing.value ? 'Сохранить' : 'Добавить'))

const load = async () => {
	loading.value = true
	try {
		items.value = await listDrivers()
		if (viewing.value) {
			viewing.value = items.value.find(d => d.id === viewing.value!.id) || null
			if (!viewing.value) viewOpen.value = false
		}
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

const closeForm = () => {
	formOpen.value = false
	resetForm()
}

const openCreate = () => {
	resetForm()
	formOpen.value = true
}

const openView = (row: CompanyDriver) => {
	viewing.value = row
	viewOpen.value = true
}

const fillDraftFromRow = (row: CompanyDriver) => {
	editingId.value = row.id
	draft.value = {
		full_name: row.full_name || '',
		phone: row.phone || '',
		license_number: row.license_number || '',
		inn: row.inn || '',
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
	if (!draft.value.full_name.trim()) {
		toast.add({ title: 'Укажите ФИО водителя', color: 'warning' })
		return
	}
	const payload = {
		full_name: draft.value.full_name.trim(),
		phone: draft.value.phone.trim() || null,
		license_number: draft.value.license_number.trim() || null,
		inn: draft.value.inn.trim() || null,
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

const setActive = async (row: CompanyDriver, isActive: boolean) => {
	if (row.is_active === isActive) return
	await updateDriver(row.id, { is_active: isActive })
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
	const row = items.value.find(d => d.id === id)
	askDelete({
		message: row
			? `Точно хотите удалить водителя «${row.full_name}»?\nЭто действие нельзя отменить.`
			: 'Точно хотите удалить водителя?\nЭто действие нельзя отменить.',
		onConfirm: async () => {
			await deleteDriver(id)
			if (editingId.value === id) closeForm()
			if (viewing.value?.id === id) {
				viewOpen.value = false
				viewing.value = null
			}
			await load()
			toast.add({ title: 'Водитель удалён', color: 'success' })
		},
	})
}
</script>

<template>
	<div class="space-y-6">
		<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-xl font-semibold text-gray-900">Водители</h1>
				<p class="text-sm text-gray-500 mt-1">Список водителей вашей компании.</p>
			</div>
			<UButton
				color="primary"
				icon="i-lucide-plus"
				label="Добавить водителя"
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
					<p class="font-medium">{{ row.full_name }}</p>
					<p class="text-sm text-gray-500">
						<span v-if="row.phone">{{ row.phone }}</span>
						<span v-if="row.license_number"> · ВУ {{ row.license_number }}</span>
						<span v-if="row.inn"> · ИНН {{ row.inn }}</span>
						<span :class="row.is_active ? 'text-green-600' : 'text-gray-400'">
							· {{ row.is_active ? 'активен' : 'неактивен' }}
						</span>
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
						:aria-label="row.is_active ? 'Выключить водителя' : 'Включить водителя'"
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
		<p v-else class="text-sm text-gray-500">Пока нет водителей — добавьте первого.</p>

		<UModal
			v-model:open="viewOpen"
			:title="viewing?.full_name || 'Водитель'"
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
							<dt class="text-gray-500">Телефон</dt>
							<dd class="font-medium text-gray-900">{{ viewing.phone || '—' }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">ВУ</dt>
							<dd class="font-medium text-gray-900">{{ viewing.license_number || '—' }}</dd>
						</div>
						<div>
							<dt class="text-gray-500">ИНН</dt>
							<dd class="font-medium text-gray-900">{{ viewing.inn || '—' }}</dd>
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
				<div class="space-y-4 p-1 sm:p-2">
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<UFormField label="ФИО" class="sm:col-span-2">
							<UInput v-model="draft.full_name" placeholder="Иванов Иван Иванович" />
						</UFormField>
						<UFormField label="Телефон">
							<UInput v-model="draft.phone" placeholder="+7…" />
						</UFormField>
						<UFormField label="ВУ / номер удостоверения">
							<UInput v-model="draft.license_number" />
						</UFormField>
						<UFormField label="ИНН">
							<UInput v-model="draft.inn" inputmode="numeric" />
						</UFormField>
						<UFormField label="Комментарий" class="sm:col-span-2">
							<UInput v-model="draft.notes" />
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
	</div>

	<ConfirmDeleteModal
		v-model:open="deleteOpen"
		:title="deleteTitle"
		:message="deleteMessage"
		:loading="deleteLoading"
		@confirm="confirmDelete"
	/>
</template>
