import type { Company } from '~/types/company'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  console.log('Search query:', query)
  
  // Sample companies data
  const manufacturers: Company[] = [
    {
      id: 1,
      name: 'ООО "ТехноПром"',
      description: 'Ведущий производитель промышленного оборудования в регионе',
      country: 'Россия',
      region: 'Московская область',
      city: 'Москва',
      federalDistrict: 'Центральный федеральный округ',
      logo: 'https://i.pinimg.com/originals/7f/cd/59/7fcd5945f9cdb726bb9b124a650f13b3.jpg',
      products: ['Станки', 'Оборудование', 'Инструменты'],
      type: 'manufacturer',
      slug: 'technoprom',
      tradeActivity: 'Продавец',
      businessType: 'Производство товаров',
      activityType: 'Производство',
      fullName: 'Общество с ограниченной ответственностью "ТехноПром"',
      inn: '1234567890',
      ogrn: '1234567890123',
      kpp: '123456789',
      registrationDate: '2020-01-01',
      legalAddress: 'г. Москва, ул. Примерная, д. 1',
      productionAddress: 'г. Москва, ул. Производственная, д. 1',
      phone: '+7 (999) 123-45-67',
      email: 'info@technoprom.ru',
      website: 'https://technoprom.ru',
      isOwner: false
    },
    {
      id: 2,
      name: 'ЗАО "МеталлСервис"',
      description: 'Производство металлоизделий и металлоконструкций',
      country: 'Россия',
      region: 'Свердловская область',
      city: 'Екатеринбург',
      federalDistrict: 'Уральский федеральный округ',
      logo: 'https://www.prosoft.ru/upload/iblock/b10/md16k0pijb116ca1lqsjh0alkug3wa0j/MasterSCADA_Avtomatizatsiya_promyshlennosti.jpg',
      products: ['Металлоконструкции', 'Металлоизделия'],
      type: 'manufacturer',
      slug: 'metallservice',
      tradeActivity: 'Продавец',
      businessType: 'Производство товаров',
      activityType: 'Производство',
      fullName: 'Закрытое акционерное общество "МеталлСервис"',
      inn: '0987654321',
      ogrn: '3210987654321',
      kpp: '987654321',
      registrationDate: '2019-01-01',
      legalAddress: 'г. Екатеринбург, ул. Металлическая, д. 1',
      productionAddress: 'г. Екатеринбург, ул. Заводская, д. 1',
      phone: '+7 (999) 765-43-21',
      email: 'info@metallservice.ru',
      website: 'https://metallservice.ru',
      isOwner: false
    }
  ]

  // Filter companies based on query parameters
  let filteredManufacturers = manufacturers

  if (query.search) {
    const search = query.search.toString().toLowerCase()
    filteredManufacturers = filteredManufacturers.filter(m => 
      m.name.toLowerCase().includes(search) ||
      m.description.toLowerCase().includes(search)
    )
  }

  if (query.product) {
    const product = query.product.toString().toLowerCase()
    filteredManufacturers = filteredManufacturers.filter(m => 
      m.products.some(p => p.toLowerCase().includes(product))
    )
  }

  console.log('Filtered companies:', filteredManufacturers)
  return filteredManufacturers
}) 