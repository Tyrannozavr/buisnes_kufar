export interface ProductsInOrder {
  name: string;
  article: number;
  quantity: number;
  units: string;
  price: number;
  amount: number;
	type?: string;
}

interface Person {
  name?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}

export interface OrderData {
	saller: Person
	buyer: Person
  orderNumber: number;
  orderDate?: string;
  comments?: string;

  products: ProductsInOrder[];

  amount?: number;
  amountWord?: string;
}
