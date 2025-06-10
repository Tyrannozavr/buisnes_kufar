import { defineEventHandler, getQuery } from 'h3'
import type { Company } from '~/types/company'

// Mock data for companies - replace with actual database call
const companies: Company[] = [
  {
    id: 1,
    name: 'ТехноПром',
    logo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    type: 'manufacturer',
    slug: 'technoprom',
    tradeActivity: 'Продавец',
    businessType: 'Производство товаров',
    activityType: 'Производство',
    description: 'Производство промышленного оборудования',
    country: 'Беларусь',
    federalDistrict: 'Минская область',
    region: 'Минская область',
    city: 'Минск',
    fullName: 'ООО "ТехноПром"',
    inn: '1234567890',
    ogrn: '1234567890123',
    kpp: '123456789',
    registrationDate: '2024-01-15',
    legalAddress: 'г. Минск, ул. Промышленная, 1',
    productionAddress: 'г. Минск, ул. Промышленная, 1',
    phone: '+375 29 123-45-67',
    email: 'info@technoprom.by',
    website: 'www.technoprom.by'
  },
  {
    id: 2,
    name: 'СтройСервис',
    logo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    type: 'manufacturer',
    slug: 'stroyservice',
    tradeActivity: 'Продавец',
    businessType: 'Производство товаров и оказание услуг',
    activityType: 'Строительство',
    description: 'Строительство и ремонт',
    country: 'Беларусь',
    federalDistrict: 'Минская область',
    region: 'Минская область',
    city: 'Минск',
    fullName: 'ООО "СтройСервис"',
    inn: '0987654321',
    ogrn: '3210987654321',
    kpp: '987654321',
    registrationDate: '2024-02-20',
    legalAddress: 'г. Минск, ул. Строителей, 5',
    productionAddress: 'г. Минск, ул. Строителей, 5',
    phone: '+375 29 765-43-21',
    email: 'info@stroyservice.by',
    website: 'www.stroyservice.by'
  }
]

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const limit = Number(query.limit) || 6

  // Get latest companies
  const data = companies.slice(0, limit)

  return data
}) 