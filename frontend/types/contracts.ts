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
  amount?: number ;
  amountWord?: string;

  products: ProductsInOrder[];
}

export interface Insert {
	purchasesStateGood: boolean
	purchasesStateService: boolean
	salesStateGood: boolean
	salesStateService: boolean
}