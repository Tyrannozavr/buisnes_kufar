export interface ProductsInOrder {
  name: string;
  article: string;
  quantity: number;
  units: string;
  price: number;
  amount: number;
	type: string;
}

interface Company {
  companyId?: number;
  sellerName?: string;
  buyerName?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}

export interface OrderData {
	seller: Company
	buyer: Company
  orderNumber: string; // номер заказа "00001"
  dealId: number; // id заказа 1
  orderDate?: string;
  comments?: string;
  amount?: number ;
  amountWord?: string;

  products: ProductsInOrder[];
}