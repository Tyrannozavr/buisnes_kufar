export interface CompanyContractItem {
	id: number
	seller_company_id: number
	buyer_company_id: number
	number: string
	date: string
}

export interface CompanyContractListResponse {
	contracts: CompanyContractItem[]
}
