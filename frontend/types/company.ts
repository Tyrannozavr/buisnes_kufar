export interface Company {
  id: number
  logo: string | null
  type: string,
  tradeActivity: 'Покупатель' | 'Продавец' | 'Покупатель и продавец'
  businessType: 'Производство товаров' | 'Оказание услуг' | 'Производство товаров и оказание услуг'
  name: string
  activityType: string
  description: string
  country: string
  federalDistrict: string
  region: string
  city: string
  fullName: string
  inn: string
  ogrn: string
  kpp: string
  registrationDate: string
  legalAddress: string
  productionAddress: string
  phone: string
  email: string
  website: string
} 