export interface ProductsInOrder {
  name: string;
  article: number;
  quantity: number;
  units: string;
  price: number;
  productAmount: number;
}

export interface OrderData {
  innSaller: number;
  sallerName: string;
  companyNameSaller: string;
  urAdressSaller: string;
  mobileNumberSaller: number;

  buyerName: string;
  companyNameBuyer: string;
  urAdressBuyer: string;
  mobileNumberBuyer: number;
  orderNumber: number;
  orderDate: string;
  comments: string;

  products: ProductsInOrder[];

  amount: number;
  amountWord: string;
}
