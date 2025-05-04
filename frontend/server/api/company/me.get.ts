import { defineEventHandler } from 'h3'

export default defineEventHandler(async (event) => {
  // TODO: Implement proper authentication
  // For now, we'll just return mock data
  return {
    id: 1,
    logo: null,
    tradeActivity: 'Продавец',
    businessType: 'Производство товаров',
    name: 'ООО "Тестовая компания"',
    activityType: 'Производство обуви',
    description: 'Описание компании',
    country: 'Россия',
    federalDistrict: 'Центральный',
    region: 'Московская область',
    city: 'Москва',
    fullName: 'Общество с ограниченной ответственностью "Тестовая компания"',
    inn: '1234567890',
    ogrn: '1234567890123',
    kpp: '123456789',
    registrationDate: '2020-01-01',
    legalAddress: 'г. Москва, ул. Тестовая, д. 1',
    productionAddress: 'г. Москва, ул. Производственная, д. 1',
    phone: '+7 (999) 123-45-67',
    email: 'test@example.com',
    website: 'https://example.com'
  }
}) 