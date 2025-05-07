export interface Company {
  id: number
  logo: string | null
  type: string,
  slug: string
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

// Type for partner company with only the required fields
export interface PartnerCompany {
  fullName: string
  slug: string
  logo: string | null
  businessType: string
  country: string
  region: string
  city: string
}