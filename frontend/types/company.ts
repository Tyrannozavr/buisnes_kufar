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

export interface CompanyDetails {
  description: string
  inn: string
  ogrn: string
  ogrnDate: string
  kpp: string
  legalAddress: string
  productionAddress: string
  phone: string
  email: string
  website: string
}

export interface CompanyStatistics {
  totalProducts: number
  totalViews: number
  monthlyViews: number
  registrationDate: string
  totalPurchases?: number
}

export interface ManufacturersSearchParams {
  search?: string
  country?: string
  federalDistrict?: string
  region?: string
  city?: string
  product?: string
}

// Define a simple manufacturer type
export interface Manufacturer {
  id: string
  logo: string | null
  name: string
  country: string
  region: string
  city: string
  description: string
  tradeActivity: string
}