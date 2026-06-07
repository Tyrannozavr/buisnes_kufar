import type { OfficialsResponse } from "./dealResponse"

export type SupplyContractEntityStatus = 'loading' | 'not_found' | 'found' | 'expired'

export interface SpecificationItemEntity {
	name: string
	article?: string | null
	quantity: number
	units: string
	price: number
	amount: number
}

export interface SpecificationEntityResponse {
	id: number
	supply_contract_id: number
	supply_contract_number?: string | null
	spec_number: string
	spec_date: string
	spec_text?: string
	spec_items: SpecificationItemEntity[]
}

export interface SupplyContractEntityResponse {
	id: number
	buyer_company_id: number
	seller_company_id: number
	number: string
	date: string
	officials_json?: OfficialsResponse[] | null
	terms_text?: string
	specifications: SpecificationEntityResponse[]
	supplier_details_check: boolean
	buyer_details_check: boolean
	cover_letter_check: boolean
}

export interface SupplyContractExistsResponse {
	is_exist: boolean
	supply_contract: SupplyContractEntityResponse | null
}

export interface SupplyContractEntityCreate {
	buyer_company_id: number
	seller_company_id: number
}

export interface SupplyContractEntityUpdate {
	officials_json?: OfficialsResponse[]
	terms_text?: string
	supplier_details_check?: boolean
	buyer_details_check?: boolean
	cover_letter_check?: boolean
}

export interface SpecificationEntityUpdate {
	spec_text?: string
	spec_items?: SpecificationItemEntity[]
}

export const SUPPLY_CONTRACT_STATUS_LABELS: Record<SupplyContractEntityStatus, string> = {
	loading: 'Проверка договора…',
	not_found: 'Договор не найден',
	found: 'Договор найден',
	expired: 'Договор недействителен',
}

export const resolveSupplyContractEntityStatus = (
	isExist: boolean,
	contract: SupplyContractEntityResponse | null | undefined,
): SupplyContractEntityStatus => {
	if (!isExist || !contract) {
		return 'not_found'
	}
	if (!contract.number?.trim() || !contract.date) {
		return 'expired'
	}
	return 'found'
}
