<script setup lang="ts">
import SupplyContractEditor from '~/components/EditorMenu/templatesEditors/SupplyContractEditor.vue'
import { Editor, TemplateElement } from '~/constants/keys'
import { useSupplyContractEntity } from '~/composables/useSupplyContractEntity'
import { useSupplyContractTemplates } from '~/composables/useSupplyContractTemplates'
import PersonSelector from '../tables/PersonSelector.vue'
import type { Company, Official } from '~/types/dealState.js'
import type { SupplyContractTemplateType } from '~/types/supplyContractTemplate'
import { useDeals } from '~/composables/useDeals'
import {
	extractInsertedSupplyContractFields,
	type InsertedSupplyContractField,
	type SupplyContractFieldKey,
} from '~/utils/supplyContractFields'

const route = useRoute()
const dealId = computed(() => Number(route.query.dealId) || null)

const coverLetterCheck = useTypedState(Editor.COVER_LETTER_CHECK, () => ref(false))
const supplierDetailsCheck = useTypedState(Editor.SUPPLIER_DETAILS_CHECK, () => ref(false))
const buyerDetailsCheck = useTypedState(Editor.BUYER_DETAILS_CHECK, () => ref(false))
const supplyContractType = useTypedState(Editor.SUPPLY_CONTRACT_TYPE, () => ref('supplyContract'))
const supplyContractOfficialsSeller = useTypedState(Editor.SUPPLY_CONTRACT_OFFICIALS_SELLER, () => ref([]))
const supplyContractSlotRevision = useState<number>(Editor.SUPPLY_CONTRACT_SLOT_REVISION, () => 0)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
const specificationHTML = useTypedState(TemplateElement.SPECIFICATION)

const {
	findDeal,
	editSellerCompany,
	editBuyerCompany,
	editPaymentTermsContract,
	editDeliveryTermsContract,
} = useDeals()
const { ensureContractForSpecification } = useSupplyContractEntity(dealId)
const currentDeal = computed(() => dealId.value ? findDeal(dealId.value) : undefined)

const activeTemplateType = computed<SupplyContractTemplateType>(() =>
	supplyContractType.value === 'supplyContract' ? 'supply_contract' : 'specification',
)

const {
	templateItems,
	defaultTemplate,
	templates,
	templatesMatchActiveType,
	applyTemplateById,
	applyDefaultIfEmpty,
	refreshTemplates,
} = useSupplyContractTemplates(activeTemplateType, dealId)

const selectedContractTemplateId = ref<number | undefined>()
const selectedSpecificationTemplateId = ref<number | undefined>()
const isSyncingTemplateSelection = ref(false)

const selectedTemplateId = computed({
	get: () =>
		activeTemplateType.value === 'supply_contract'
			? selectedContractTemplateId.value
			: selectedSpecificationTemplateId.value,
	set: (value: number | undefined) => {
		if (activeTemplateType.value === 'supply_contract') {
			selectedContractTemplateId.value = value
			return
		}
		selectedSpecificationTemplateId.value = value
	},
})

const syncHtmlFromDealForActiveTab = () => {
	const deal = dealId.value ? findDeal(dealId.value) : undefined
	if (!deal) return

	if (activeTemplateType.value === 'supply_contract') {
		supplyContractHTML.value = deal.supplyContract.supplyContractText ?? ''
		return
	}

	specificationHTML.value = deal.supplyContract.specificationText ?? ''
}

const syncSelectedTemplateFromDeal = () => {
	const deal = dealId.value ? findDeal(dealId.value) : undefined
	if (!deal) return

	isSyncingTemplateSelection.value = true

	const syncForType = (type: SupplyContractTemplateType) => {
		const storedId = type === 'supply_contract'
			? deal.supplyContract.templateSupplyContract
			: deal.supplyContract.templateSpecification
		const parsedId = storedId ? Number(storedId) : NaN
		const resolvedId = Number.isFinite(parsedId) && parsedId > 0 ? parsedId : undefined

		if (type === 'supply_contract') {
			selectedContractTemplateId.value = resolvedId
			return
		}

		selectedSpecificationTemplateId.value = resolvedId
	}

	syncForType('supply_contract')
	syncForType('specification')

	if (activeTemplateType.value === 'supply_contract' && !selectedContractTemplateId.value && defaultTemplate.value?.type === 'supply_contract') {
		selectedContractTemplateId.value = defaultTemplate.value.id
	}

	if (activeTemplateType.value === 'specification' && !selectedSpecificationTemplateId.value && defaultTemplate.value?.type === 'specification') {
		selectedSpecificationTemplateId.value = defaultTemplate.value.id
	}

	nextTick(() => {
		isSyncingTemplateSelection.value = false
	})
}

const applyDefaultForCurrentTab = () => {
	if (route.query.role !== 'seller') return
	if (!templatesMatchActiveType.value) return

	const deal = dealId.value ? findDeal(dealId.value) : undefined
	if (!deal) return

	if (activeTemplateType.value === 'supply_contract') {
		const currentText = deal.supplyContract.supplyContractText || supplyContractHTML.value
		if (currentText?.trim()) return
		const applied = applyDefaultIfEmpty(currentText)
		if (applied) selectedContractTemplateId.value = applied.id
		return
	}

	const currentText = deal.supplyContract.specificationText || specificationHTML.value
	if (currentText?.trim()) return
	const applied = applyDefaultIfEmpty(currentText)
	if (applied) selectedSpecificationTemplateId.value = applied.id
}

watch(
	() => [templates.value, defaultTemplate.value, dealId.value, route.query.role, activeTemplateType.value],
	() => {
		syncSelectedTemplateFromDeal()
		applyDefaultForCurrentTab()
	},
	{ immediate: true },
)

const handleTemplateSelect = (templateId: number | undefined) => {
	if (isSyncingTemplateSelection.value) return
	selectedTemplateId.value = templateId
	applyTemplateById(templateId)
}

const handleSelectContractTab = () => {
	supplyContractType.value = 'supplyContract'
	syncHtmlFromDealForActiveTab()
	syncSelectedTemplateFromDeal()
}

const handleSelectSpecificationTab = async () => {
	const allowed = await ensureContractForSpecification()
	if (!allowed) return
	supplyContractType.value = 'specification'
	syncHtmlFromDealForActiveTab()
	syncSelectedTemplateFromDeal()
}

const handleTemplateSaved = async (templateId: number) => {
	selectedTemplateId.value = templateId
	await refreshTemplates()
}

const insertedSupplyContractFields = computed(() =>
	extractInsertedSupplyContractFields([
		supplyContractHTML.value,
		specificationHTML.value,
	]),
)

const visibleInsertedFields = computed(() =>
	insertedSupplyContractFields.value.filter((field) =>
		field.fieldKey !== 'officialName' || field.party === 'buyer',
	),
)

const editableCompanyFieldKeys = new Set<SupplyContractFieldKey>([
	'companyName',
	'companyType',
	'city',
	'fullName',
	'ogrn',
	'inn',
	'kpp',
	'legalAddress',
	'productionAddress',
	'phone',
	'email',
])

const getCompanyByInsertedField = (field: InsertedSupplyContractField) =>
	field.party === 'seller' ? currentDeal.value?.seller : currentDeal.value?.buyer

const fieldInputValues = reactive<Record<string, string>>({})
const sellerOfficialDraft = reactive({
	position: '',
	name: '',
})
let slotRevisionTimeout: ReturnType<typeof setTimeout> | null = null

const scheduleSlotRevision = () => {
	if (slotRevisionTimeout) clearTimeout(slotRevisionTimeout)
	slotRevisionTimeout = setTimeout(() => {
		supplyContractSlotRevision.value += 1
		slotRevisionTimeout = null
	}, 250)
}

const getStoredFieldValue = (field: InsertedSupplyContractField): string => {
	if (field.party === 'contract') {
		if (field.fieldKey === 'paymentTerms') return currentDeal.value?.bill.paymentTermsContract ?? ''
		if (field.fieldKey === 'deliveryTerms') return currentDeal.value?.bill.deliveryTermsContract ?? ''
		return ''
	}

	if (field.fieldKey === 'officialName') {
		return field.party === 'buyer' ? currentDeal.value?.buyer.ownerName ?? '' : ''
	}

	const company = getCompanyByInsertedField(field)
	const value = company?.[field.fieldKey as keyof Company]
	return value == null ? '' : String(value)
}

const syncFieldInputValues = () => {
	const activeFieldIds = new Set(visibleInsertedFields.value.map((field) => field.id))

	visibleInsertedFields.value.forEach((field) => {
		if (fieldInputValues[field.id] === undefined) {
			fieldInputValues[field.id] = getStoredFieldValue(field)
		}
	})

	Object.keys(fieldInputValues).forEach((fieldId) => {
		if (!activeFieldIds.has(fieldId)) delete fieldInputValues[fieldId]
	})
}

watch(
	() => [visibleInsertedFields.value, dealId.value],
	() => syncFieldInputValues(),
	{ deep: true, immediate: true },
)

watch(
	() => supplyContractOfficialsSeller.value[0],
	(official) => {
		sellerOfficialDraft.position = official?.position ?? ''
		sellerOfficialDraft.name = official?.name ?? ''
	},
	{ deep: true, immediate: true },
)

const commitFieldValue = (field: InsertedSupplyContractField, value: string) => {
	if (!dealId.value) return

	if (field.party === 'contract') {
		if (field.fieldKey === 'paymentTerms') {
			editPaymentTermsContract(dealId.value, value)
			scheduleSlotRevision()
			return
		}

		if (field.fieldKey === 'deliveryTerms') {
			editDeliveryTermsContract(dealId.value, value)
			scheduleSlotRevision()
		}
		return
	}

	if (field.fieldKey === 'officialName' && field.party === 'buyer') {
		editBuyerCompany(dealId.value, { ownerName: value })
		scheduleSlotRevision()
		return
	}

	if (!editableCompanyFieldKeys.has(field.fieldKey)) return

	const payload = {
		[field.fieldKey]: field.fieldKey === 'inn'
			? Number(value) || undefined
			: value,
	} as Company

	if (field.party === 'seller') {
		editSellerCompany(dealId.value, payload)
	} else {
		editBuyerCompany(dealId.value, payload)
	}

	scheduleSlotRevision()
}

const handleFieldInput = (field: InsertedSupplyContractField, value: string | number) => {
	const normalizedValue = String(value ?? '')
	fieldInputValues[field.id] = normalizedValue
}

const commitFieldInput = (field: InsertedSupplyContractField) => {
	commitFieldValue(field, fieldInputValues[field.id] ?? '')
}

const updateSellerOfficial = (patch: Partial<Official>) => {
	const current = supplyContractOfficialsSeller.value[0] as Official | undefined
	const sellerCompanyId = currentDeal.value?.seller.companyId ?? 0

	supplyContractOfficialsSeller.value = [{
		id: current?.id ?? 0,
		companyId: current?.companyId ?? sellerCompanyId,
		name: current?.name ?? '',
		position: current?.position ?? '',
		isBase: current?.isBase ?? false,
		baseDocument: current?.baseDocument ?? '',
		baseDocumentName: current?.baseDocumentName ?? '',
		...patch,
	}]
	scheduleSlotRevision()
}

const handleSellerOfficialInput = (field: 'position' | 'name', value: string | number) => {
	const normalizedValue = String(value ?? '')
	sellerOfficialDraft[field] = normalizedValue
}

const commitSellerOfficialInput = () => {
	updateSellerOfficial({
		position: sellerOfficialDraft.position,
		name: sellerOfficialDraft.name,
	})
}

const addPerson = (person: Official) => {
	if (supplyContractOfficialsSeller.value.some((p) => p.id === person.id)) {
		return useToast().add({ title: 'Должностное лицо уже добавлено', color: 'warning' })
	}
	supplyContractOfficialsSeller.value = [person]
	sellerOfficialDraft.position = person.position
	sellerOfficialDraft.name = person.name
	scheduleSlotRevision()
}

onBeforeUnmount(() => {
	if (slotRevisionTimeout) clearTimeout(slotRevisionTimeout)
})
</script>

<template>
	<div class="flex flex-col gap-3">
		<div class="mb-2 flex gap-4">
			<button
				type="button"
				class="cursor-pointer"
				:class="{ 'font-bold text-blue-500': supplyContractType === 'supplyContract' }"
				@click="handleSelectContractTab"
			>
				Договор
			</button>
			<button
				type="button"
				class="cursor-pointer"
				:class="{ 'font-bold text-blue-500': supplyContractType === 'specification' }"
				@click="handleSelectSpecificationTab"
			>
				Спецификация
			</button>
		</div>

		<div :disabled="isDisabled" v-if="supplyContractType === 'supplyContract'" class="">
			<SupplyContractEditor
				:label="'Редактор договора поставки'"
				template-type="supply_contract"
				v-model:selected-template-id="selectedTemplateId"
				@saved="handleTemplateSaved"
			/>
		</div>
		<div :disabled="isDisabled" v-else-if="supplyContractType === 'specification'">
			<SupplyContractEditor
				:label="'Редактор спецификации'"
				template-type="specification"
				v-model:selected-template-id="selectedTemplateId"
				@saved="handleTemplateSaved"
			/>
		</div>

		<USelect
			:disabled="isDisabled"
			placeholder="Выберите шаблон"
			:items="templateItems"
			:model-value="selectedTemplateId"
			@update:model-value="handleTemplateSelect"
		/>

		<UModal>
			<UButton
				:disabled="isDisabled"
				label="Редактировать данные договора поставки"
				variant="subtle"
				color="neutral"
			/>
			<template #header>
				<h3 class="text-lg font-semibold">Редактор данных договора поставки</h3>
			</template>
			<template #body>
				<div class="flex flex-col gap-4">
					<div v-if="!insertedSupplyContractFields.length" class="rounded-md bg-gray-50 p-3 text-sm text-gray-500">
						Вставьте поля через кнопку «Реквизиты» в редакторе, затем они появятся здесь для редактирования.
					</div>

					<div class="flex flex-col gap-2 rounded-md border border-gray-200 p-3">
						<p class="text-sm font-semibold">ДОЛЖНОСТЬ + ФИО (Поставщик)</p>
						<PersonSelector :isDisabled="isDisabled" :isBase="false" @addPerson="addPerson($event)" />
						<UInput
							:disabled="isDisabled"
							:model-value="sellerOfficialDraft.position"
							placeholder="Должность"
							@update:model-value="handleSellerOfficialInput('position', $event)"
							@blur="commitSellerOfficialInput"
							@change="commitSellerOfficialInput"
						/>
						<UInput
							:disabled="isDisabled"
							:model-value="sellerOfficialDraft.name"
							placeholder="ФИО"
							@update:model-value="handleSellerOfficialInput('name', $event)"
							@blur="commitSellerOfficialInput"
							@change="commitSellerOfficialInput"
						/>
					</div>

					<div
						v-for="field in visibleInsertedFields"
						:key="field.id"
						class="flex flex-col gap-1"
					>
						<label class="text-sm font-medium">{{ field.label }}</label>
						<UInput
							:disabled="isDisabled"
							:model-value="fieldInputValues[field.id] ?? ''"
							:placeholder="field.label"
							@update:model-value="handleFieldInput(field, $event)"
							@blur="commitFieldInput(field)"
							@change="commitFieldInput(field)"
						/>
					</div>
				</div>
			</template>
		</UModal>

		<UCheckbox :disabled="isDisabled" label="Колонтитул" size="xl" v-model="coverLetterCheck" />
		<UCheckbox :disabled="isDisabled" label="Реквизиты поставщика" size="xl" v-model="supplierDetailsCheck" />
		<UCheckbox :disabled="isDisabled" label="Реквизиты покупателя" size="xl" v-model="buyerDetailsCheck" />
	</div>
</template>
