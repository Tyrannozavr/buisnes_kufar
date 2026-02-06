export interface BuyerTableItems {
	dealNumber: string
	date: string
	sallerCompany: string
	state?: string
	bill?: string
	supplyContract?: string
	closingDocuments?: string
	othersDocument?: string
}

export interface SellerTableItems {
  dealNumber: string;
  date: string;
  buyerCompany: string;
  state?: string;
  bill?: string;
  supplyContract?: string;
  closingDocuments?: string;
  othersDocument?: string;
}