<script setup lang="ts">
import type { CompanyFillAddress, FillAddressKind } from '~/types/fillAddress'
import { useFillAddressesApi } from '~/api/me/fillAddresses'

const props = defineProps<{
	kind: FillAddressKind
	title: string
	hint: string
}>()

const {
	listFillAddresses,
	createFillAddress,
	updateFillAddress,
	setFillAddressDefault,
	deleteFillAddress,
} = useFillAddressesApi()

const toast = useToast()
const addresses = ref<CompanyFillAddress[]>([])
const loading = ref(false)
const draftAddress = ref('')
const editingId = ref<number | null>(null)
const editText = ref('')

const load = async () => {
	loading.value = true
	try {
		addresses.value = await listFillAddresses(props.kind)
	} catch (e: any) {
		toast.add({
			title: 'Ошибка',
			description: e?.message || 'Не удалось загрузить адреса',
			color: 'error',
		})
	} finally {
		loading.value = false
	}
}

onMounted(load)

const addAddress = async () => {
	const text = draftAddress.value.trim()
	if (!text) {
		toast.add({ title: 'Введите адрес', color: 'warning' })
		return
	}
	loading.value = true
	try {
		await createFillAddress({ kind: props.kind, address: text })
		draftAddress.value = ''
		await load()
		toast.add({ title: 'Адрес добавлен', color: 'success' })
	} catch (e: any) {
		toast.add({
			title: 'Ошибка',
			description: e?.data?.detail || e?.message || 'Не удалось добавить адрес',
			color: 'error',
		})
	} finally {
		loading.value = false
	}
}

const setDefault = async (id: number) => {
	loading.value = true
	try {
		await setFillAddressDefault(id)
		await load()
	} catch (e: any) {
		toast.add({
			title: 'Ошибка',
			description: e?.message || 'Не удалось назначить адрес по умолчанию',
			color: 'error',
		})
	} finally {
		loading.value = false
	}
}

const startEdit = (row: CompanyFillAddress) => {
	editingId.value = row.id
	editText.value = row.address
}

const saveEdit = async () => {
	if (editingId.value == null) return
	const text = editText.value.trim()
	if (!text) {
		toast.add({ title: 'Введите адрес', color: 'warning' })
		return
	}
	loading.value = true
	try {
		await updateFillAddress(editingId.value, { address: text })
		editingId.value = null
		await load()
		toast.add({ title: 'Адрес обновлён', color: 'success' })
	} catch (e: any) {
		toast.add({
			title: 'Ошибка',
			description: e?.message || 'Не удалось сохранить адрес',
			color: 'error',
		})
	} finally {
		loading.value = false
	}
}

const remove = async (id: number) => {
	loading.value = true
	try {
		await deleteFillAddress(id)
		await load()
		toast.add({ title: 'Адрес удалён', color: 'success' })
	} catch (e: any) {
		toast.add({
			title: 'Ошибка',
			description: e?.message || 'Не удалось удалить адрес',
			color: 'error',
		})
	} finally {
		loading.value = false
	}
}
</script>

<template>
	<section class="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
		<div>
			<h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
			<p class="mt-1 text-sm text-gray-500">{{ hint }}</p>
		</div>

		<div v-if="loading && !addresses.length" class="py-6 text-center text-sm text-gray-500">
			Загрузка…
		</div>

		<ul v-else class="space-y-3">
			<li
				v-for="row in addresses"
				:key="row.id"
				class="flex flex-col gap-2 rounded-md border border-gray-100 bg-gray-50/80 px-3 py-3 sm:flex-row sm:items-center sm:justify-between"
			>
				<div class="flex-1 min-w-0">
					<template v-if="editingId === row.id">
						<UInput v-model="editText" class="w-full" @keyup.enter="saveEdit" />
					</template>
					<template v-else>
						<p class="text-sm text-gray-900 break-words">{{ row.address }}</p>
						<p v-if="row.is_default" class="mt-1 text-xs font-medium text-primary-600">
							По умолчанию
						</p>
					</template>
				</div>
				<div class="flex flex-wrap items-center gap-2 shrink-0">
					<template v-if="editingId === row.id">
						<UButton size="sm" color="primary" :loading="loading" @click="saveEdit">
							Сохранить
						</UButton>
						<UButton
							size="sm"
							color="neutral"
							variant="ghost"
							@click="editingId = null"
						>
							Отмена
						</UButton>
					</template>
					<template v-else>
						<UButton
							v-if="!row.is_default"
							size="sm"
							color="neutral"
							variant="soft"
							:loading="loading"
							@click="setDefault(row.id)"
						>
							По умолчанию
						</UButton>
						<UButton
							size="sm"
							color="neutral"
							variant="ghost"
							icon="i-heroicons-pencil-square"
							@click="startEdit(row)"
						/>
						<UButton
							size="sm"
							color="error"
							variant="ghost"
							icon="i-heroicons-trash"
							:loading="loading"
							@click="remove(row.id)"
						/>
					</template>
				</div>
			</li>
			<li v-if="!addresses.length" class="text-sm text-gray-500 py-2">
				Адресов пока нет — добавьте первый ниже.
			</li>
		</ul>

		<div class="flex flex-col gap-2 sm:flex-row sm:items-end">
			<UFormField label="Новый адрес" class="flex-1 w-full">
				<UInput
					v-model="draftAddress"
					placeholder="Введите адрес"
					class="w-full"
					@keyup.enter="addAddress"
				/>
			</UFormField>
			<UButton color="primary" :loading="loading" class="sm:mb-0.5" @click="addAddress">
				Добавить
			</UButton>
		</div>
	</section>
</template>
