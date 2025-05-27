import type { Company } from '~/types/company'

export const companies: Company[] = [
  {
    id: 1,
    logo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    type: 'manufacturer',
    slug: 'technoprom',
    tradeActivity: 'Продавец',
    businessType: 'Производство товаров',
    name: 'ТехноПром',
    activityType: 'Производство',
    description: 'Производство промышленного оборудования',
    country: 'Россия',
    federalDistrict: 'Центральный',
    region: 'Московская область',
    city: 'Москва',
    fullName: 'ООО "ТехноПром"',
    inn: '1234567890',
    ogrn: '1234567890123',
    kpp: '123456789',
    registrationDate: '2020-01-01',
    legalAddress: 'г. Москва, ул. Примерная, д. 1',
    productionAddress: 'г. Москва, ул. Производственная, д. 1',
    phone: '+7 (999) 123-45-67',
    email: 'info@technoprom.ru',
    website: 'https://technoprom.ru'
  },
  {
    id: 2,
    logo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    type: 'manufacturer',
    slug: 'stroyservice',
    tradeActivity: 'Продавец',
    businessType: 'Производство товаров и оказание услуг',
    name: 'СтройСервис',
    activityType: 'Строительство',
    description: 'Строительство и отделочные работы',
    country: 'Россия',
    federalDistrict: 'Центральный',
    region: 'Московская область',
    city: 'Москва',
    fullName: 'ООО "СтройСервис"',
    inn: '0987654321',
    ogrn: '3210987654321',
    kpp: '987654321',
    registrationDate: '2021-02-15',
    legalAddress: 'г. Москва, ул. Строительная, д. 2',
    productionAddress: 'г. Москва, ул. Строительная, д. 2',
    phone: '+7 (999) 765-43-21',
    email: 'info@stroyservice.ru',
    website: 'https://stroyservice.ru'
  }
]

export default defineEventHandler(() => {
  return companies
}) 