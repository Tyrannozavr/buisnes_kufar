import { useQueryCache } from '@pinia/colada'
import { Editor } from '~/constants/keys'
import { QueryKeys } from '~/constants/queryKeys'
import { useDeals } from '~/composables/useDeals'
import {
	contractConditionTemplatesQuery,
	useCreateContractConditionTemplateQuery,
	useUpdateContractConditionTemplateQuery,
} from '~/queries/purchases'
import type {
	ContractConditionTemplate,
	ContractConditionTemplateType,
} from '~/types/contractConditionTemplate'

const TEMPLATE_VALUE_BY_NAME: Record<string, 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'> = {
	'Стандартный, доставка Поставщика': 'standard-delivery-supplier',
	'Стандартный, доставка Покупателя': 'standard-delivery-buyer',
}

export const contractTermsSelectValueForTemplate = (
	template: ContractConditionTemplate,
): 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom' =>
	TEMPLATE_VALUE_BY_NAME[template.name] ?? 'custom'

export const useContractConditionTemplates = (
	templateType: Ref<ContractConditionTemplateType>,
	dealId?: Ref<number | null | undefined>,
) => {
	const queryCache = useQueryCache()
	const toast = useToast()
	const {
		editContractTermsContract,
		editContractTermsTextContract,
		editContractTermsOffer,
		editContractTermsTextOffer,
	} = useDeals()

	const contractTermsTextContract = useTypedState(Editor.CONTRACT_TERMS_TEXT_CONTRACT)
	const contractTermsTextOffer = useTypedState(Editor.CONTRACT_TERMS_TEXT_OFFER)
	const contractTermsContract = useTypedState(Editor.CONTRACT_TERMS_CONTRACT)
	const contractTermsOffer = useTypedState(Editor.CONTRACT_TERMS_OFFER)

	const { data: templates, status } = useQuery(() =>
		contractConditionTemplatesQuery({ type: templateType.value }),
	)

	const templateItems = computed(() => [
		...(templates.value ?? []).map((template: ContractConditionTemplate) => ({
			label: template.is_default ? `${template.name} (по умолчанию)` : template.name,
			value: template.id,
		})),
		{ label: 'Свой шаблон', value: 'custom' as const },
	])

	const selectItemsForDealField = computed(() => {
		const fromApi = (templates.value ?? []).map((template) => {
			const value = contractTermsSelectValueForTemplate(template)
			return {
				label: template.is_default ? `${template.name} (по умолчанию)` : template.name,
				value,
			}
		})
		const seen = new Set<string>()
		const unique = fromApi.filter((item) => {
			if (seen.has(item.value) && item.value !== 'custom') return false
			seen.add(item.value)
			return true
		})
		if (!unique.some((item) => item.value === 'custom')) {
			unique.push({ label: 'Свой шаблон', value: 'custom' })
		}
		return unique
	})

	const defaultTemplate = computed(() =>
		(templates.value ?? []).find((template) => template.is_default) ?? null,
	)

	const templatesMatchActiveType = computed(() => {
		const list = templates.value ?? []
		if (!list.length) return false
		return list.every((template) => template.type === templateType.value)
	})

	const refreshTemplates = async () => {
		await queryCache.invalidateQueries({ key: [QueryKeys.CONTRACT_CONDITION_TEMPLATES, templateType.value] })
	}

	const applyTemplate = (template: ContractConditionTemplate) => {
		if (template.type !== templateType.value) return

		const selectValue = contractTermsSelectValueForTemplate(template)
		const selectItem = {
			value: selectValue,
			label: template.name,
		}

		if (template.type === 'bill_contract') {
			contractTermsTextContract.value = template.content_text
			contractTermsContract.value = selectItem
		} else {
			contractTermsTextOffer.value = template.content_text
			contractTermsOffer.value = selectItem
		}

		const resolvedDealId = dealId?.value
		if (!resolvedDealId) return

		if (template.type === 'bill_contract') {
			editContractTermsContract(resolvedDealId, selectValue)
			editContractTermsTextContract(resolvedDealId, template.content_text)
		} else {
			editContractTermsOffer(resolvedDealId, selectValue)
			editContractTermsTextOffer(resolvedDealId, template.content_text)
		}
	}

	const applyTemplateById = (templateId: number | undefined | null) => {
		if (!templateId) return
		const template = (templates.value ?? []).find(
			(item) => item.id === templateId && item.type === templateType.value,
		)
		if (template) applyTemplate(template)
	}

	const applyTextToTypedState = (contentText: string) => {
		if (templateType.value === 'bill_contract') {
			contractTermsTextContract.value = contentText
		} else {
			contractTermsTextOffer.value = contentText
		}

		const resolvedDealId = dealId?.value
		if (!resolvedDealId) return

		if (templateType.value === 'bill_contract') {
			editContractTermsTextContract(resolvedDealId, contentText)
		} else {
			editContractTermsTextOffer(resolvedDealId, contentText)
		}
	}

	const applyDefaultIfEmpty = (currentText: string | undefined | null) => {
		if (currentText?.trim()) return null
		if (!templatesMatchActiveType.value) return null
		const template = defaultTemplate.value
		if (!template || template.type !== templateType.value) return null
		applyTemplate(template)
		return template
	}

	const { createContractConditionTemplate } = useCreateContractConditionTemplateQuery()
	const { updateContractConditionTemplate } = useUpdateContractConditionTemplateQuery()

	const saveTemplate = async ({
		templateId,
		name,
		contentText,
		isDefault,
	}: {
		templateId?: number | null
		name: string
		contentText: string
		isDefault: boolean
	}) => {
		const trimmedName = name.trim()
		if (!trimmedName) {
			toast.add({ title: 'Укажите название шаблона', color: 'warning' })
			return null
		}

		try {
			let saved: ContractConditionTemplate | undefined
			if (templateId) {
				saved = await updateContractConditionTemplate(
					templateId,
					{
						name: trimmedName,
						content_text: contentText,
						is_default: isDefault,
					},
					templateType.value,
				)
			} else {
				saved = await createContractConditionTemplate({
					type: templateType.value,
					name: trimmedName,
					content_text: contentText,
					is_default: isDefault,
				})
			}

			if (saved) {
				applyTextToTypedState(contentText)
			}
			return saved ?? null
		} catch (err: unknown) {
			const detail =
				(err as { data?: { detail?: string } })?.data?.detail
				|| (err as Error)?.message
				|| ''
			toast.add({
				title: 'Не удалось сохранить шаблон',
				description:
					detail === 'Template with this name already exists'
						? 'Шаблон с таким названием уже есть — выберите его в списке или задайте другое имя'
						: detail || undefined,
				color: 'error',
			})
			return null
		}
	}

	return {
		templates,
		templateItems,
		selectItemsForDealField,
		defaultTemplate,
		templatesMatchActiveType,
		status,
		refreshTemplates,
		applyTemplate,
		applyTemplateById,
		applyTextToTypedState,
		applyDefaultIfEmpty,
		saveTemplate,
	}
}
