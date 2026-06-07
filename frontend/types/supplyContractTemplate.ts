export type SupplyContractTemplateType = 'supply_contract' | 'specification'

export interface SupplyContractTemplate {
	id: number
	company_id: number
	type: SupplyContractTemplateType
	name: string
	content_html: string
	is_default: boolean
	created_at: string
	updated_at: string
}

export interface SupplyContractTemplateCreate {
	type: SupplyContractTemplateType
	name: string
	content_html: string
	is_default?: boolean
}

export interface SupplyContractTemplateUpdate {
	name?: string
	content_html?: string
	is_default?: boolean
}
