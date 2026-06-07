import { useQueryCache } from '@pinia/colada'
import { TemplateElement } from '~/constants/keys'
import { QueryKeys } from '~/constants/queryKeys'
import { useDeals } from '~/composables/useDeals'
import {
	supplyContractTemplatesQuery,
	useCreateSupplyContractTemplateQuery,
	useUpdateSupplyContractTemplateQuery,
} from '~/queries/purchases'
import type { SupplyContractTemplate, SupplyContractTemplateType } from '~/types/supplyContractTemplate'

export const useSupplyContractTemplates = (
	templateType: Ref<SupplyContractTemplateType>,
	dealId?: Ref<number | null | undefined>,
) => {
	const queryCache = useQueryCache()
	const toast = useToast()
	const { editSupplyContractTemplate, editSupplyContractSpecificationTemplate, editSupplyContractText, editSupplyContractSpecificationText } = useDeals()
	const supplyContractHTML = useTypedState(TemplateElement.SUPPLY_CONTRACT)
	const specificationHTML = useTypedState(TemplateElement.SPECIFICATION)

	const { data: templates, status } = useQuery(() =>
		supplyContractTemplatesQuery({ type: templateType.value }),
	)

	const templateItems = computed(() =>
		(templates.value ?? []).map((template: SupplyContractTemplate) => ({
			label: template.is_default ? `${template.name} (по умолчанию)` : template.name,
			value: template.id,
		})),
	)

	const defaultTemplate = computed(() =>
		(templates.value ?? []).find((template) => template.is_default) ?? null,
	)

	const templatesMatchActiveType = computed(() => {
		const list = templates.value ?? []
		if (!list.length) return false
		return list.every((template) => template.type === templateType.value)
	})

	const refreshTemplates = async () => {
		await queryCache.invalidateQueries({ key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATES, templateType.value] })
	}

	const applyTemplate = (template: SupplyContractTemplate) => {
		if (template.type !== templateType.value) return

		if (template.type === 'supply_contract') {
			supplyContractHTML.value = template.content_html
		} else {
			specificationHTML.value = template.content_html
		}

		const resolvedDealId = dealId?.value
		if (!resolvedDealId) return

		if (template.type === 'supply_contract') {
			editSupplyContractTemplate(resolvedDealId, String(template.id))
			editSupplyContractText(resolvedDealId, template.content_html)
		} else {
			editSupplyContractSpecificationTemplate(resolvedDealId, String(template.id))
			editSupplyContractSpecificationText(resolvedDealId, template.content_html)
		}
	}

	const applyTemplateById = (templateId: number | undefined | null) => {
		if (!templateId) return
		const template = (templates.value ?? []).find(
			(item) => item.id === templateId && item.type === templateType.value,
		)
		if (template) applyTemplate(template)
	}

	const applyDefaultIfEmpty = (currentHtml: string | undefined | null) => {
		if (currentHtml?.trim()) return null
		if (!templatesMatchActiveType.value) return null
		const template = defaultTemplate.value
		if (!template || template.type !== templateType.value) return null
		applyTemplate(template)
		return template
	}

	const { createSupplyContractTemplate } = useCreateSupplyContractTemplateQuery()
	const { updateSupplyContractTemplate } = useUpdateSupplyContractTemplateQuery()

	const saveTemplate = async ({
		templateId,
		name,
		contentHtml,
		isDefault,
	}: {
		templateId?: number | null
		name: string
		contentHtml: string
		isDefault: boolean
	}) => {
		const trimmedName = name.trim()
		if (!trimmedName) {
			toast.add({ title: 'Укажите название шаблона', color: 'warning' })
			return null
		}

		try {
			if (templateId) {
				return await updateSupplyContractTemplate(
					templateId,
					{
						name: trimmedName,
						content_html: contentHtml,
						is_default: isDefault,
					},
					templateType.value,
				)
			}

			return await createSupplyContractTemplate({
				type: templateType.value,
				name: trimmedName,
				content_html: contentHtml,
				is_default: isDefault,
			})
		} catch {
			toast.add({ title: 'Не удалось сохранить шаблон', color: 'error' })
			return null
		}
	}

	return {
		templates,
		templateItems,
		defaultTemplate,
		templatesMatchActiveType,
		status,
		refreshTemplates,
		applyTemplate,
		applyTemplateById,
		applyDefaultIfEmpty,
		saveTemplate,
	}
}
