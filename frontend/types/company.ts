import type { LocationItem } from './location'

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
  officials?: Array<{
    position: string
    fullName: string
  }>
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
export interface CompanyShort {
  id: string
  logo: string | null
  name: string
  country: string
  region: string
  city: string
  description: string
  tradeActivity: string
}

export interface CompanyInfo {
  companyName: string
  companyLogo: string
}

export interface CompanyFormState {
    name: string
    inn: string
    kpp: string
    ogrn: string
    registrationDate: string
    legalAddress: string
    productionAddress: string
    country: LocationItem | undefined
    federalDistrict: LocationItem | undefined
    region: LocationItem | undefined
    city: LocationItem | undefined
    countryOptions: LocationItem[]
    federalDistrictOptions: LocationItem[]
    regionOptions: LocationItem[]
    cityOptions: LocationItem[]
}

export interface CompanyFormProps {
    modelValue: CompanyFormState
    loading?: boolean
    error?: string | null
}

export interface CompanyOfficial {
  position: string
  fullName: string
}

export interface CompanyDataFormState {
  inn: string
  kpp: string
  ogrn: string
  registrationDate: string
  country: LocationItem | undefined
  federalDistrict: LocationItem | undefined
  region: LocationItem | undefined
  city: LocationItem | undefined
  productionAddress: string
  officials: CompanyOfficial[]
  tradeActivity: string
  businessType: string
  activityType: string
  position: string
  companyName: string
  companyDescription: string
  companyWebsite: string
  companyLogo: string
  companyAddress: string
  companyPhone: string
  companyEmail: string
}

export interface CompanyDataFormProps {
  company: Company
  loading?: boolean
}

