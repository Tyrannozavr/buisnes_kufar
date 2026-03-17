export interface ProductsInOrder {
  name: string;
  article: string;
  quantity: number;
  units: string;
  price: number;
  amount: number;
}

interface CompanyOrder {
	companyId?: number
	ownerName?: string
	phone?: string
	companyName?: string
	legalAddress?: string
	inn?: number
}

export interface OrderData {
	seller: CompanyOrder
	buyer: CompanyOrder
	orderNumber: string // номер заказа "00001"
	dealId: number // id заказа 1
	orderDate?: string
	comments?: string
	amount?: number
	amountWord?: string

	products: ProductsInOrder[]
}