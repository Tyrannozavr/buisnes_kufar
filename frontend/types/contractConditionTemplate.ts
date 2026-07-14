export type ContractConditionTemplateType = 'bill_contract' | 'bill_offer'

export interface ContractConditionTemplate {
	id: number
	company_id: number
	type: ContractConditionTemplateType
	name: string
	content_text: string
	is_default: boolean
	created_at: string
	updated_at: string
}

export interface ContractConditionTemplateCreate {
	type: ContractConditionTemplateType
	name: string
	content_text: string
	is_default?: boolean
}

export interface ContractConditionTemplateUpdate {
	name?: string
	content_text?: string
	is_default?: boolean
}
