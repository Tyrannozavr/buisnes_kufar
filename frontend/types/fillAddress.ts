export type FillAddressKind = 'loading' | 'receiving'

export interface CompanyFillAddress {
	id: number
	company_id: number
	kind: FillAddressKind
	address: string
	is_default: boolean
	created_at: string
	updated_at?: string | null
}

export interface CompanyFillAddressCreate {
	kind: FillAddressKind
	address: string
	is_default?: boolean
}

export interface CompanyFillAddressUpdate {
	address?: string
	is_default?: boolean
}
