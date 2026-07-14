<template>
	<div>
		<USelectMenu
			placeholder="Тип документа"
			:items="billTypeOptions"
			:model-value="billType"
			:disabled="isDisabled"
			default-value="Счет на оплату"
			class="w-full"
			@update:model-value="onBillTypeSelect"
		/>

		<div :hidden="hiddenForBuyer" class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Основание" v-model="reasonCheck" size="xl" class="mt-2" />
		</div>

		<div :hidden="hiddenForBuyer" class="mb-2">
			<UCheckbox :disabled="isDisabled" label="Ставка НДС" v-model="vatRateCheck" size="xl" class="mb-2" />
			<USelectMenu
				v-if="vatRateCheck"
				:disabled="isDisabled"
				placeholder="Ставка НДС"
				:items="vatRateOptions"
				v-model="sellerVatRate"
				class="w-full"
				/>
		</div>

		<div v-if="billType.value === 'bill'" :hidden="hiddenForBuyer" class="flex flex-col gap-2">
			<UCheckbox :disabled="isDisabled" label="Дополнительная информация" v-model="additionalInfoCheck" size="xl" />

			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheck" size="xl" class="w-fit"/>
			<div class="flex gap-1" v-if="paymentTermsCheck">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTerms">
			</div>
		</div>
		
		<div v-if="billType.value === 'bill-contract'" :hidden="hiddenForBuyer" class="flex flex-col gap-2">
			<div class="flex gap-2 justify-between">
				<UCheckbox :disabled="isDisabled" label="Условия договора" v-model="contractTermsCheckContract" size="xl"/>

				<ContractTermsEditor />
			</div>

			<USelectMenu
				v-if="contractTermsCheckContract"
				:disabled="isDisabled"
				placeholder="Условия договора"
				:items="contractTermsOptionsContract"
				v-model="contractTermsContract"
				class="w-full"
				/>

			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheckContract" size="xl"/>
			<div class="flex gap-1" v-if="paymentTermsCheckContract">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTermsContract" default-value="3">
			</div>

			<UCheckbox :disabled="isDisabled" label="Срок поставки" v-model="deliveryTermsCheckContract" size="xl"/>
			<div class="flex gap-1" v-if="deliveryTermsCheckContract">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки поставки" class="w-50 p-1 border rounded-lg" v-model="deliveryTermsContract" default-value="10">
			</div>

			<UCheckbox :disabled="isDisabled" label="Реквизиты поставщика" v-model="billSupplierDetailsCheck" size="xl" />
			<UCheckbox :disabled="isDisabled" label="Реквизиты покупателя" v-model="billBuyerDetailsCheck" size="xl" />
		</div>

		<div v-if="billType.value === 'bill-offer'" :hidden="hiddenForBuyer" class="flex flex-col gap-2">
			<UCheckbox :disabled="isDisabled" label="Дополнительная информация" v-model="additionalInfoCheckOffer" size="xl"/>

			<div class="flex gap-2 justify-between">
				<UCheckbox :disabled="isDisabled" label="Условия договора" v-model="contractTermsCheckOffer" size="xl"/>

				<ContractTermsEditor />
			</div>

			<USelectMenu
				v-if="contractTermsCheckOffer"
				:disabled="isDisabled"
				placeholder="Условия договора"
				:items="contractTermsOptionsOffer"
				v-model="contractTermsOffer"
				class="w-full"
				/>

			<UCheckbox :disabled="isDisabled" label="Срок оплаты" v-model="paymentTermsCheckOffer" size="xl"/>
			<div class="flex gap-1" v-if="paymentTermsCheckOffer">
				<label class="w-full self-center">Рабочих дней - </label>
				<input type="number" :disabled="isDisabled" placeholder="Введите сроки оплаты" class="w-50 p-1 border rounded-lg" v-model="paymentTermsOffer" default-value="3">
			</div>

			<UTooltip
				text="В счёте-оферте срок поставки не задаётся — только срок оплаты. Смените тип на «Счет-договор», если нужен срок поставки."
			>
				<span class="inline-flex w-fit cursor-not-allowed">
					<UCheckbox
						disabled
						label="Срок поставки"
						:model-value="false"
						size="xl"
					/>
				</span>
			</UTooltip>
		</div>

		<UModal
			v-model:open="billTypeConfirmOpen"
			title="Сменить тип документа?"
			:ui="{
				header: 'pe-10',
			}"
		>
			<template #body>
				<p class="mb-4 text-sm text-gray-600">
					При смене типа документа форма другого бланка не будет видна. Продолжить?
				</p>
				<div class="flex flex-row justify-between gap-2">
					<UButton
						label="Отмена"
						icon="i-lucide-x"
						color="neutral"
						variant="subtle"
						class="w-1/2"
						@click="cancelBillTypeChange"
					/>
					<UButton
						label="Продолжить"
						icon="i-lucide-check"
						color="success"
						variant="subtle"
						class="w-1/2"
						@click="confirmBillTypeChange"
					/>
				</div>
			</template>
		</UModal>
	</div>
</template>

<script setup lang="ts">
import type { SelectMenuItem } from '@nuxt/ui';
import { Editor } from '~/constants/keys';
import { VAT_RATE_OPTIONS } from '~/constants/vatRate';
import { useDeals } from '~/composables/useDeals';
import { useCompanyBillRequisites } from '~/composables/useCompanyBillRequisites';
import { useBillFillState } from '~/composables/useBillFillState';
import {
	contractTermsSelectValueForTemplate,
	useContractConditionTemplates,
} from '~/composables/useContractConditionTemplates'
import type { ContractConditionTemplateType } from '~/types/contractConditionTemplate'
import ContractTermsEditor from '~/components/EditorMenu/templatesEditors/BillContractTermsEditor.vue'

defineProps<{
	hiddenForBuyer?: boolean
}>()

const DEFAULT_PAYMENT_TERMS_DAYS = '3'

const BILL_TYPE_OPTIONS: { label: string; value: 'bill' | 'bill-contract' | 'bill-offer' }[] = [
	{ label: 'Счет на оплату', value: 'bill' },
	{ label: 'Счет-договор', value: 'bill-contract' },
	{ label: 'Счет-оферта', value: 'bill-offer' },
]

const BILL_TYPE_BY_VALUE = Object.fromEntries(
	BILL_TYPE_OPTIONS.map((item) => [item.value, item]),
) as Record<'bill' | 'bill-contract' | 'bill-offer', { label: string; value: 'bill' | 'bill-contract' | 'bill-offer' }>

const STATIC_CONTRACT_TERMS_OPTIONS: SelectMenuItem[] = [
	{ label: 'Стандартный, доставка Поставщика', value: 'standard-delivery-supplier' },
	{ label: 'Стандартный, доставка Покупателя', value: 'standard-delivery-buyer' },
	{ label: 'Свой шаблон', value: 'custom' },
]

const { findDeal, editBillDocumentType } = useDeals()
const { loadBillRequisites } = useCompanyBillRequisites()
const route = useRoute()
const isDisabled = useTypedState(Editor.IS_DISABLED)
const billAwaitingFill = useBillFillState().billAwaitingFill

const billTypeOptions = ref<SelectMenuItem[]>([...BILL_TYPE_OPTIONS])
const vatRateOptions = VAT_RATE_OPTIONS

//initial values
const initialReasonCheck = ref(false)
const initialVatRateCheck = ref(false)
const initialSellerVatRate = ref(0)

//bill-payment(счет-оплата)
const initialPaymentTerms = ref('')
const initialPaymentTermsCheck = ref(false)
const initialAdditionalInfoCheck = ref(false)

//bill-contract
const initialPaymentTermsContract = ref('')
const initialDeliveryTermsContract = ref('')
const initialContractTermsContract = ref<{ value: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'; label: string }>({ value: 'standard-delivery-supplier', label: 'Стандартный, доставка Поставщика' })
const initialPaymentTermsCheckContract = ref(false)
const initialDeliveryTermsCheckContract = ref(false)
const initialContractTermsCheckContract = ref(false)
const initialBillSupplierDetailsCheck = ref(true)
const initialBillBuyerDetailsCheck = ref(true)

//bill-offer
const initialPaymentTermsOffer = ref('')
const initialContractTermsOffer = ref<{ value: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'; label: string }>({ value: 'standard-delivery-supplier', label: 'Стандартный, доставка Поставщика' })
const initialContractTermsCheckOffer = ref(false)
const initialPaymentTermsCheckOffer = ref(false)
const initialAdditionalInfoCheckOffer = ref(false)
const initialDeliveryTermsCheckOffer = ref(false)

const dealForEditor = computed(() =>
	findDeal(Number(route.query.dealId))
)

//bill-general — до useContractConditionTemplates (иначе TDZ: billType before initialization)
const billType = useTypedState(Editor.BILL_TYPE, () => ref({ ...BILL_TYPE_BY_VALUE.bill }))
const reasonCheck = useTypedState(Editor.REASON_CHECK, () => initialReasonCheck)
const vatRateCheck = useTypedState(Editor.VAT_RATE_CHECK, () => initialVatRateCheck)
const sellerVatRate = useTypedState(Editor.VAT_RATE, () => initialSellerVatRate)

//bill-payment(счет-оплата)
const paymentTerms = useTypedState(Editor.PAYMENT_TERMS, () => initialPaymentTerms)
const paymentTermsCheck = useTypedState(Editor.PAYMENT_TERMS_CHECK, () => initialPaymentTermsCheck)
const additionalInfoCheck = useTypedState(Editor.ADDITIONAL_INFO_CHECK, () => initialAdditionalInfoCheck)

//bill-contract
const paymentTermsContract = useTypedState(Editor.PAYMENT_TERMS_CONTRACT, () => initialPaymentTermsContract)
const deliveryTermsContract = useTypedState(Editor.DELIVERY_TERMS_CONTRACT, () => initialDeliveryTermsContract)
const contractTermsContract = useTypedState(Editor.CONTRACT_TERMS_CONTRACT, () => initialContractTermsContract)
const paymentTermsCheckContract = useTypedState(Editor.PAYMENT_TERMS_CHECK_CONTRACT, () => initialPaymentTermsCheckContract)
const deliveryTermsCheckContract = useTypedState(Editor.DELIVERY_TERMS_CHECK_CONTRACT, () => initialDeliveryTermsCheckContract)
const contractTermsCheckContract = useTypedState(Editor.CONTRACT_TERMS_CHECK_CONTRACT, () => initialContractTermsCheckContract)
const billSupplierDetailsCheck = useTypedState(Editor.BILL_SUPPLIER_DETAILS_CHECK, () => initialBillSupplierDetailsCheck)
const billBuyerDetailsCheck = useTypedState(Editor.BILL_BUYER_DETAILS_CHECK, () => initialBillBuyerDetailsCheck)

//bill-offer
const paymentTermsOffer = useTypedState(Editor.PAYMENT_TERMS_OFFER, () => initialPaymentTermsOffer)
const contractTermsOffer = useTypedState(Editor.CONTRACT_TERMS_OFFER, () => initialContractTermsOffer)
const contractTermsCheckOffer = useTypedState(Editor.CONTRACT_TERMS_CHECK_OFFER, () => initialContractTermsCheckOffer)
const paymentTermsCheckOffer = useTypedState(Editor.PAYMENT_TERMS_CHECK_OFFER, () => initialPaymentTermsCheckOffer)
const additionalInfoCheckOffer = useTypedState(Editor.ADDITIONAL_INFO_CHECK_OFFER, () => initialAdditionalInfoCheckOffer)
const deliveryTermsCheckOffer = useTypedState(Editor.DELIVERY_TERMS_CHECK_OFFER, () => initialDeliveryTermsCheckOffer)

const dealIdRef = computed(() => Number(route.query.dealId) || null)
const conditionTemplateType = computed<ContractConditionTemplateType>(() =>
	billType.value?.value === 'bill-offer' ? 'bill_offer' : 'bill_contract',
)
const {
	selectItemsForDealField: contractTermsOptionsFromApi,
	templates: conditionTemplates,
	applyTemplate,
} = useContractConditionTemplates(conditionTemplateType, dealIdRef)

const contractTermsTextContract = useTypedState(Editor.CONTRACT_TERMS_TEXT_CONTRACT, () => ref(''))
const contractTermsTextOffer = useTypedState(Editor.CONTRACT_TERMS_TEXT_OFFER, () => ref(''))

const contractTermsOptionsContract = computed(() =>
	contractTermsOptionsFromApi.value.length
		? contractTermsOptionsFromApi.value
		: STATIC_CONTRACT_TERMS_OPTIONS,
)
const contractTermsOptionsOffer = computed(() =>
	contractTermsOptionsFromApi.value.length
		? contractTermsOptionsFromApi.value
		: STATIC_CONTRACT_TERMS_OPTIONS,
)

/** Если выбран стандартный шаблон, а текст state пустой — подтянуть content_text из API */
watch(
	() => [
		billType.value?.value,
		contractTermsContract.value?.value,
		contractTermsOffer.value?.value,
		conditionTemplates.value,
		contractTermsTextContract.value,
		contractTermsTextOffer.value,
	],
	() => {
		const docType = billType.value?.value
		if (docType !== 'bill-contract' && docType !== 'bill-offer') return
		const selectValue =
			docType === 'bill-offer'
				? contractTermsOffer.value?.value
				: contractTermsContract.value?.value
		if (!selectValue || selectValue === 'custom') return
		const currentText =
			docType === 'bill-offer'
				? contractTermsTextOffer.value
				: contractTermsTextContract.value
		if ((currentText ?? '').trim()) return
		const template = (conditionTemplates.value ?? []).find(
			(item) => contractTermsSelectValueForTemplate(item) === selectValue,
		)
		if (template) applyTemplate(template)
	},
	{ deep: true },
)

const clearState = useTypedState(Editor.CLEAR_STATE)

const confirmedBillType = ref({ ...BILL_TYPE_BY_VALUE.bill })
const pendingBillType = ref<{ label: string; value: 'bill' | 'bill-contract' | 'bill-offer' } | null>(null)
const billTypeConfirmOpen = ref(false)

const setBillTypeQuietly = (next: { label: string; value: 'bill' | 'bill-contract' | 'bill-offer' }) => {
	billType.value = { ...next }
	confirmedBillType.value = { ...next }
}

/** Только ручной выбор в селекте — не при загрузке сделки / fillBillData */
const onBillTypeSelect = (next: unknown) => {
	const selected = next as { label?: string; value?: 'bill' | 'bill-contract' | 'bill-offer' } | null
	if (!selected?.value) return
	if (selected.value === confirmedBillType.value.value) {
		billType.value = { label: selected.label ?? BILL_TYPE_BY_VALUE[selected.value].label, value: selected.value }
		return
	}
	pendingBillType.value = {
		label: selected.label ?? BILL_TYPE_BY_VALUE[selected.value].label,
		value: selected.value,
	}
	billTypeConfirmOpen.value = true
}

const confirmBillTypeChange = async () => {
	if (!pendingBillType.value) {
		billTypeConfirmOpen.value = false
		return
	}
	setBillTypeQuietly(pendingBillType.value)
	const dealId = Number(route.query.dealId)
	if (dealId) {
		await editBillDocumentType(dealId, pendingBillType.value.value)
	}
	pendingBillType.value = null
	billTypeConfirmOpen.value = false
}

const cancelBillTypeChange = () => {
	pendingBillType.value = null
	billTypeConfirmOpen.value = false
	setBillTypeQuietly(confirmedBillType.value)
}

/** Внешняя синхронизация (Bill.fillBillData / deal watch) — без модалки */
watch(billType, (next) => {
	if (billTypeConfirmOpen.value || !next?.value) return
	if (next.value === confirmedBillType.value.value) return
	confirmedBillType.value = { label: next.label, value: next.value }
}, { deep: true })

watch(paymentTermsCheck, (checked) => {
	if (checked && !paymentTerms.value) {
		paymentTerms.value = DEFAULT_PAYMENT_TERMS_DAYS
	}
})

watch(
	() => clearState.value,
	(clearing) => {
		if (!clearing) return
		reasonCheck.value = false
		vatRateCheck.value = false
		paymentTermsCheck.value = false
		paymentTerms.value = ''
		additionalInfoCheck.value = true
	},
)

const resolveSellerVatFromLk = async (deal: NonNullable<ReturnType<typeof findDeal>>) => {
	const lk = await loadBillRequisites(deal.seller.companyId)
	return lk?.party.vatRate ?? deal.seller.vatRate ?? 0
}

const resolveContractTermsItem = (
	value: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom' | undefined,
) => {
	if (value === 'standard-delivery-buyer') {
		return { value: 'standard-delivery-buyer' as const, label: 'Стандартный, доставка Покупателя' }
	}
	if (value === 'custom') {
		return { value: 'custom' as const, label: 'Свой шаблон' }
	}
	return { value: 'standard-delivery-supplier' as const, label: 'Стандартный, доставка Поставщика' }
}

//задаем initial значения по данным сделки
watch(
	[() => route.query.dealId, dealForEditor, billAwaitingFill],
	async () => {
		const deal = dealForEditor.value
		if (!deal) return

		const sellerVatFromLk = await resolveSellerVatFromLk(deal)
		const useLkDefaults = billAwaitingFill.value || !deal.bill.number

		const documentType = deal.bill.documentType ?? 'bill'
		const mappedType = BILL_TYPE_BY_VALUE[documentType] ?? BILL_TYPE_BY_VALUE.bill
		setBillTypeQuietly(mappedType)

		//bill-general
		initialReasonCheck.value = deal.bill.reason !== '' ? true : false
		if (useLkDefaults) {
			initialVatRateCheck.value = sellerVatFromLk > 0
			initialSellerVatRate.value = sellerVatFromLk
		} else {
			initialVatRateCheck.value = deal.amountWithVatRate
			initialSellerVatRate.value = deal.amountWithVatRate
				? (deal.seller.vatRate ?? sellerVatFromLk)
				: sellerVatFromLk
		}

		//bill-payment(счет-оплата)
		initialPaymentTerms.value = deal.bill.paymentTerms ?? ''
		initialPaymentTermsCheck.value = deal.bill.paymentTerms !== '' ? true : false
		initialAdditionalInfoCheck.value = true

		//bill-contract
		initialPaymentTermsContract.value = deal.bill.paymentTermsContract ?? ''
		initialDeliveryTermsContract.value = deal.bill.deliveryTermsContract ?? ''
		initialContractTermsContract.value = resolveContractTermsItem(deal.bill.contractTermsContract)
		initialPaymentTermsCheckContract.value = deal.bill.paymentTermsContract !== '' ? true : false
		initialDeliveryTermsCheckContract.value = deal.bill.deliveryTermsContract !== '' ? true : false
		initialContractTermsCheckContract.value = deal.bill.contractTermsTextContract !== '' ? true : false
		initialBillSupplierDetailsCheck.value = deal.bill.supplierDetailsCheck ?? true
		initialBillBuyerDetailsCheck.value = deal.bill.buyerDetailsCheck ?? true
		billSupplierDetailsCheck.value = initialBillSupplierDetailsCheck.value
		billBuyerDetailsCheck.value = initialBillBuyerDetailsCheck.value

		//bill-offer
		initialPaymentTermsOffer.value = deal.bill.paymentTermsOffer ?? ''
		initialContractTermsOffer.value = resolveContractTermsItem(deal.bill.contractTermsOffer)
		initialContractTermsCheckOffer.value = deal.bill.contractTermsTextOffer !== '' ? true : false
		initialPaymentTermsCheckOffer.value = deal.bill.paymentTermsOffer !== '' ? true : false
		initialAdditionalInfoCheckOffer.value = deal.bill.additionalInfoOffer !== '' ? true : false
		initialDeliveryTermsCheckOffer.value = false
		deliveryTermsCheckOffer.value = false
	},
	{ immediate: true }
)


//убираем галки, если значение в поле пустое
watch(() => [
	paymentTerms.value,
	paymentTermsContract.value,
	paymentTermsOffer.value,
], () => {
	if (Number(paymentTerms.value) <= 0) {
		paymentTerms.value = '0'
		paymentTermsCheck.value = false
	}
	if (Number(paymentTermsContract.value) <= 0) {
		paymentTermsContract.value = '0'
		paymentTermsCheckContract.value = false
	}
	if (Number(paymentTermsOffer.value) <= 0) {
		paymentTermsOffer.value = '0'
		paymentTermsCheckOffer.value = false
	}
}, { deep: true, immediate: true})
</script>
