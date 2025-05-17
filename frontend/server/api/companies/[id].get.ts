import type { Company } from '~/types/company'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // Sample company data
  const company: Company = {
    id: id,
    name: 'ООО "ТехноПром"',
    description: 'Ведущий производитель промышленного оборудования в регионе. Специализируемся на производстве станков и автоматизированных линий.',
    inn: '1234567890',
    kpp: '123456789',
    ogrn: '1234567890123',
    registrationDate: '2020-01-15',
    legalAddress: 'г. Москва, ул. Промышленная, д. 1',
    productionAddress: 'г. Москва, ул. Заводская, д. 15',
    phone: '+7 (495) 123-45-67',
    email: 'info@technoprom.ru',
    website: 'https://technoprom.ru',
    isOwner: false,
    logo: '/images/company-logo.png',
    coverImage: '/images/company-cover.jpg'
  }

  return company
}) 