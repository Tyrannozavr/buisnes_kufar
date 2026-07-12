<template>
	<div class="max-w-full">
		<div class="bg-white shadow rounded-lg p-4 space-y-4">
			<div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
				<h2 class="text-lg font-medium text-gray-900">Договоры</h2>
				<UButton color="primary" icon="i-lucide-plus" @click="openCreateModal">
					Добавить договор
				</UButton>
			</div>

			<p v-if="isLoading" class="text-sm text-neutral-500" role="status">
				Загрузка договоров…
			</p>

			<p v-else-if="!contracts.length" class="text-sm text-neutral-500">
				Нет договоров с контрагентами. Добавьте договор — он появится в диалоге «Создать счет».
			</p>

			<UTable
				v-else
				:data="contracts"
				:columns="columns"
				class="max-h-[28rem] overflow-y-auto"
			/>
		</div>

		<UModal v-model:open="isFormOpen" :title="formTitle">
			<template #body>
				<div class="space-y-4 p-4">
					<UFormField v-if="!editingContract" label="Контрагент">
						<USelect
							v-model="form.counterpartyId"
							:items="counterpartyOptions"
							:loading="isCounterpartiesLoading"
							placeholder="Выберите контрагента"
						/>
						<p
							v-if="!isCounterpartiesLoading && !counterpartyOptions.length"
							class="mt-1 text-xs text-amber-600"
						>
							Контрагенты подтягиваются из сделок в «Продажи» / «Закупки» и из разделов «Покупатели» / «Поставщики».
							Если список пуст — обновите страницу или проверьте, что вы вошли как продавец с активными сделками.
						</p>
					</UFormField>

					<UFormField v-if="!editingContract" label="Ваша роль в договоре">
						<USelect
							v-model="form.relation"
							:items="relationOptions"
							value-key="value"
							label-key="label"
						/>
					</UFormField>

					<UFormField label="Номер договора">
						<UInput
							v-model="form.number"
							:readonly="!editingContract"
							:loading="isNextNumberLoading"
							placeholder="00001"
						/>
						<p v-if="!editingContract" class="mt-1 text-xs text-neutral-500">
							Номер присваивается автоматически (маска 00000, сброс ежегодно).
						</p>
					</UFormField>

					<UFormField label="Дата договора">
						<UInput v-model="form.date" type="date" />
					</UFormField>

					<div class="flex justify-end gap-2">
						<UButton color="neutral" variant="outline" @click="isFormOpen = false">
							Отмена
						</UButton>
						<UButton color="primary" :loading="isSaving" @click="saveContract">
							Сохранить
						</UButton>
					</div>
				</div>
			</template>
		</UModal>
	</div>
</template>

<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui"
import { useQuery, useQueryCache } from "@pinia/colada"
import { getBuyers, getSuppliers, getPartners } from "~/api/company"
import { usePurchasesApi } from "~/api/purchases"
import { buyerDealsQuery, sellerDealsQuery } from "~/queries/purchases"
import { QueryKeys } from "~/constants/queryKeys"
import type {
	CompanyContractCreatePayload,
	CompanyContractItem,
	CompanyContractUpdatePayload,
} from "~/types/companyContract"
import type { PartnerCompany } from "~/types/company"
import type { BuyerDealResponse, SellerDealResponse } from "~/types/dealResponse"

definePageMeta({ layout: "profile" })

const toast = useToast()
const queryCache = useQueryCache()
const purchasesApi = usePurchasesApi()
const UButton = resolveComponent("UButton")

const { data: contractsData, state: contractsState, refetch } = useQuery({
	key: () => [QueryKeys.COMPANY_CONTRACTS, "all"],
	query: () => purchasesApi.getCompanyContracts(),
})

const { data: sellerDeals, state: sellerDealsState } = useQuery({
	key: () => [QueryKeys.SELLER_DEALS, 0, 100, "contracts"],
	query: () => sellerDealsQuery({ limit: 100 }).query(),
})

const { data: buyerDeals, state: buyerDealsState } = useQuery({
	key: () => [QueryKeys.BUYER_DEALS, 0, 100, "contracts"],
	query: () => buyerDealsQuery({ limit: 100 }).query(),
})

const contracts = computed(() => contractsData.value?.contracts ?? [])
const isLoading = computed(() => contractsState.value.status === "pending")

const {
	data: buyers,
	refresh: refreshBuyers,
	pending: buyersPending,
} = await getBuyers(1, 100)
const {
	data: suppliers,
	refresh: refreshSuppliers,
	pending: suppliersPending,
} = await getSuppliers(1, 100)
const {
	data: partners,
	refresh: refreshPartners,
	pending: partnersPending,
} = await getPartners(1, 100)

const isCounterpartiesLoading = computed(
	() =>
		buyersPending.value ||
		suppliersPending.value ||
		partnersPending.value ||
		sellerDealsState.value.status === "pending" ||
		buyerDealsState.value.status === "pending",
)

const addCounterparty = (
	map: Map<number, string>,
	companyId?: number,
	name?: string,
) => {
	if (!companyId) return
	const label = (name ?? "").trim() || `Контрагент #${companyId}`
	map.set(companyId, label)
}

const counterpartyOptions = computed(() => {
	const map = new Map<number, string>()

	for (const company of [
		...(buyers.value ?? []),
		...(suppliers.value ?? []),
		...(partners.value ?? []),
	] as PartnerCompany[]) {
		addCounterparty(map, company.id, company.fullName)
	}

	for (const deal of (sellerDeals.value ?? []) as SellerDealResponse[]) {
		addCounterparty(map, deal.buyer_company_id, deal.buyer_name)
	}

	for (const deal of (buyerDeals.value ?? []) as BuyerDealResponse[]) {
		addCounterparty(map, deal.seller_company_id, deal.supplier_name)
	}

	return [...map.entries()]
		.map(([value, label]) => ({ label, value }))
		.sort((a, b) => a.label.localeCompare(b.label, "ru"))
})

onMounted(() => {
	void refreshBuyers()
	void refreshSuppliers()
	void refreshPartners()
})

const relationOptions = [
	{ value: "as_seller", label: "Я — поставщик, контрагент — покупатель" },
	{ value: "as_buyer", label: "Я — покупатель, контрагент — поставщик" },
]

const isFormOpen = ref(false)
const isSaving = ref(false)
const isNextNumberLoading = ref(false)
const editingContract = ref<CompanyContractItem | null>(null)

const form = reactive({
	counterpartyId: undefined as number | undefined,
	relation: "as_seller" as "as_seller" | "as_buyer",
	number: "",
	date: "",
})

const formTitle = computed(() =>
	editingContract.value ? "Редактировать договор" : "Добавить договор",
)

const loadNextNumber = async () => {
	if (editingContract.value) return
	if (form.relation === "as_buyer" && !form.counterpartyId) {
		form.number = ""
		return
	}

	isNextNumberLoading.value = true
	try {
		const preview = await purchasesApi.getCompanyContractNextNumber({
			relation: form.relation,
			counterparty_company_id:
				form.relation === "as_buyer" ? form.counterpartyId : undefined,
		})
		form.number = preview.number
		form.date = preview.date.slice(0, 10)
	} catch {
		form.number = ""
		form.date = new Date().toISOString().slice(0, 10)
	} finally {
		isNextNumberLoading.value = false
	}
}

watch(
	() => [form.relation, form.counterpartyId] as const,
	() => {
		if (!isFormOpen.value || editingContract.value) return
		void loadNextNumber()
	},
)

const formatDate = (iso: string) => {
	const date = new Date(iso)
	if (Number.isNaN(date.getTime())) return iso
	return date.toLocaleDateString("ru-RU")
}

const openCreateModal = () => {
	editingContract.value = null
	form.counterpartyId = undefined
	form.relation = "as_seller"
	form.number = ""
	form.date = ""
	isFormOpen.value = true
	void loadNextNumber()
}

const openEditModal = (contract: CompanyContractItem) => {
	editingContract.value = contract
	form.number = contract.number
	form.date = contract.date.slice(0, 10)
	isFormOpen.value = true
}

const invalidateContracts = async () => {
	await queryCache.invalidateQueries({ key: [QueryKeys.COMPANY_CONTRACTS] })
	await refetch()
}

const saveContract = async () => {
	if (!form.date) {
		toast.add({ title: "Укажите дату", color: "warning" })
		return
	}

	isSaving.value = true
	try {
		if (editingContract.value) {
			if (!form.number.trim()) {
				toast.add({ title: "Укажите номер", color: "warning" })
				return
			}
			const body: CompanyContractUpdatePayload = {
				number: form.number.trim(),
				date: new Date(form.date).toISOString(),
			}
			await purchasesApi.updateCompanyContract(editingContract.value.id, body)
			toast.add({ title: "Договор обновлён", color: "success" })
		} else {
			if (!form.counterpartyId) {
				toast.add({ title: "Выберите контрагента", color: "warning" })
				return
			}
			const body: CompanyContractCreatePayload = {
				counterparty_company_id: form.counterpartyId,
				date: new Date(form.date).toISOString(),
				relation: form.relation,
			}
			if (form.number.trim()) {
				body.number = form.number.trim()
			}
			await purchasesApi.createCompanyContract(body)
			toast.add({ title: "Договор добавлен", color: "success" })
		}
		isFormOpen.value = false
		await invalidateContracts()
	} catch {
		toast.add({ title: "Не удалось сохранить договор", color: "error" })
	} finally {
		isSaving.value = false
	}
}

const removeContract = async (contract: CompanyContractItem) => {
	if (!confirm(`Удалить договор № ${contract.number}?`)) return
	try {
		await purchasesApi.deleteCompanyContract(contract.id)
		toast.add({ title: "Договор удалён", color: "success" })
		await invalidateContracts()
	} catch {
		toast.add({ title: "Не удалось удалить договор", color: "error" })
	}
}

const columns: TableColumn<CompanyContractItem>[] = [
	{ accessorKey: "number", header: "Номер" },
	{
		accessorKey: "date",
		header: "Дата",
		cell: ({ row }) => formatDate(row.original.date),
	},
	{
		accessorKey: "counterparty_name",
		header: "Контрагент",
	},
	{
		id: "actions",
		header: "",
		cell: ({ row }) =>
			h("div", { class: "flex gap-2 justify-end" }, [
				h(UButton, {
					size: "xs",
					color: "neutral",
					variant: "subtle",
					label: "Изменить",
					onClick: () => openEditModal(row.original),
				}),
				h(UButton, {
					size: "xs",
					color: "error",
					variant: "soft",
					label: "Удалить",
					onClick: () => removeContract(row.original),
				}),
			]),
	},
]
</script>
