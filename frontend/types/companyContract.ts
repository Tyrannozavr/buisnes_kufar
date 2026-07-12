export interface CompanyContractItem {
	id: number
	seller_company_id: number
	buyer_company_id: number
	number: string
	date: string
	counterparty_company_id: number
	counterparty_name: string
	counterparty_role: "buyer" | "seller"
}

export interface CompanyContractListResponse {
	contracts: CompanyContractItem[]
}

export interface CompanyContractCreatePayload {
	counterparty_company_id: number
	number: string
	date: string
	relation: "as_seller" | "as_buyer"
}

export interface CompanyContractUpdatePayload {
	number?: string
	date?: string
}
