export interface BuyerTableItems {
	dealNumber: string
	date: string
	sellerCompany: string
	status?: string
	bill?: string
	contract?: string
	act?: string
	supplyContract?: string
	accompanyingDocuments?: string
	invoice?: string
	othersDocument?: string
}

export interface SellerTableItems {
  dealNumber: string;
  date: string;
  buyerCompany: string;
  status?: string;
  bill?: string;
  contract?: string;
  act?: string;
  supplyContract?: string;
  accompanyingDocuments?: string;
  invoice?: string;
  othersDocument?: string;
}