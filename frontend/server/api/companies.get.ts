import { defineEventHandler } from 'h3'
import type { Company } from '~/types'

// Mock data for companies
const companies: Company[] = [
  {
    id: '1',
    name: 'ООО "ТехноПром"',
    logo: '/images/companies/techprom.png',
    type: 'manufacturer',
    activity: 'Производство промышленного оборудования',
    description: 'Ведущий производитель промышленного оборудования в России',
    country: 'Россия',
    region: 'Московская область',
    city: 'Москва',
    fullName: 'Общество с ограниченной ответственностью "ТехноПром"',
    inn: '1234567890',
    ogrn: '1234567890123',
    kpp: '123456789',
    registrationDate: '2010-01-15',
    legalAddress: 'г. Москва, ул. Промышленная, д. 1',
    productionAddress: 'г. Москва, ул. Заводская, д. 10',
    phone: '+7 (495) 123-45-67',
    email: 'info@techprom.ru',
    website: 'www.techprom.ru'
  },
  {
    id: '2',
    name: 'СтройСервис',
    logo: '/images/companies/stroyservice.png',
    type: 'service',
    activity: 'Строительные услуги',
    description: 'Комплексные строительные услуги под ключ',
    country: 'Россия',
    region: 'Санкт-Петербург',
    city: 'Санкт-Петербург',
    fullName: 'ООО "СтройСервис"',
    inn: '0987654321',
    ogrn: '3210987654321',
    kpp: '987654321',
    registrationDate: '2015-03-20',
    legalAddress: 'г. Санкт-Петербург, ул. Строителей, д. 5',
    productionAddress: 'г. Санкт-Петербург, ул. Строителей, д. 5',
    phone: '+7 (812) 987-65-43',
    email: 'info@stroyservice.ru',
    website: 'www.stroyservice.ru'
  },
  {
    id: '3',
    name: 'ИнноТех',
    logo: '/images/companies/innotech.png',
    type: 'manufacturer',
    activity: 'Разработка и производство электроники',
    description: 'Инновационные решения в области электроники и автоматизации',
    country: 'Россия',
    region: 'Новосибирская область',
    city: 'Новосибирск',
    fullName: 'ООО "ИнноТех"',
    inn: '5678901234',
    ogrn: '5678901234567',
    kpp: '567890123',
    registrationDate: '2018-07-10',
    legalAddress: 'г. Новосибирск, ул. Инновационная, д. 15',
    productionAddress: 'г. Новосибирск, ул. Технопарковая, д. 3',
    phone: '+7 (383) 456-78-90',
    email: 'contact@innotech.ru',
    website: 'www.innotech.ru'
  }
]

export default defineEventHandler(() => {
  // Simulate a slight delay to mimic real API behavior
  return new Promise<Company[]>((resolve) => {
    setTimeout(() => {
      resolve(companies)
    }, 300)
  })
})