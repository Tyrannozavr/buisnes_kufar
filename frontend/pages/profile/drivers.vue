<script setup lang="ts">
import type { CompanyDriver } from '~/types/fleet'
import { useFleetApi } from '~/api/me/fleet'

definePageMeta({
	layout: 'profile',
	title: 'Водители',
})

const { listDrivers, createDriver, updateDriver, deleteDriver } = useFleetApi()
const toast = useToast()
const items = ref<CompanyDriver[]>([])
const loading = ref(false)
const draft = ref({
	full_name: '',
	phone: '',
	license_number: '',
	notes: '',
})

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

const add = async () => {
	if (!draft.value.full_name.trim()) {
		toast.add({ title: 'Укажите ФИО водителя', color: 'warning' })
		return
	}
	loading.value = true
	try {
		await createDriver({
			full_name: draft.value.full_name.trim(),
			phone: draft.value.phone.trim() || null,
			license_number: draft.value.license_number.trim() || null,
			notes: draft.value.notes.trim() || null,
			is_active: true,
		})
		draft.value = { full_name: '', phone: '', license_number: '', notes: '' }
		await load()
		toast.add({ title: 'Водитель добавлен', color: 'success' })
	} catch (e: any) {
		toast.add({ title: 'Не удалось добавить', description: e?.data?.detail || e?.message, color: 'error' })
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
				<span class="font-medium">Добавить водителя</span>
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
			<div class="mt-4">
				<UButton label="Добавить" color="primary" :loading="loading" @click="add" />
			</div>
		</UCard>

		<ul v-if="items.length" class="space-y-2">
			<li
				v-for="row in items"
				:key="row.id"
				class="border border-gray-200 rounded-lg p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
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
				<div class="flex gap-2">
					<UButton size="sm" color="neutral" variant="soft" :label="row.is_active ? 'Выключить' : 'Включить'" @click="toggleActive(row)" />
					<UButton size="sm" color="error" variant="ghost" label="Удалить" @click="remove(row.id)" />
				</div>
			</li>
		</ul>
		<p v-else class="text-sm text-gray-500">Пока нет водителей — добавьте первого.</p>
	</div>
</template>
