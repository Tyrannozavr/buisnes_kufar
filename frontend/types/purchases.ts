export interface TableGoods {
	dealNumber: string
	date: string
	sallerCompany: string
	state?: string
	bill?: string
	supplyContract?: string
	accompanyingDocuments?: string
	invoice?: string
	othersDocument?: string
}

export interface TableServices {
	dealNumber: string
	date: string
	sallerCompany: string
	state?: string
	bill?: string
	contract?: string,
	act?: string,
	invoice?: string,
	othersDocument?: string,
}
