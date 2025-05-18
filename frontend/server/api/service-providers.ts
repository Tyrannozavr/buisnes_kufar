import { defineEventHandler } from 'h3'
import type { CompanyShort } from "~/types/company"

// Mock data for service providers
const serviceProviders: CompanyShort[] = [
  {
    id: '1',
    logo: 'https://avatars.mds.yandex.net/i?id=407da9c99230ee5d885503cbe903871f26be070d-5104820-images-thumbs&n=13',
    description: 'Провайдер комплексных IT-услуг и решений для бизнеса',
    tradeActivity: 'Поставщик услуг',
    country: 'Россия',
    region: 'Московская область',
    city: 'Москва',
    name: 'Service Provider A',
  },
  {
    id: '2',
    logo: 'https://www.masterlogistica.es/wp-content/uploads/2022/01/marketing-de-afiliados-guia-completa-2048x924.png',
    description: 'Консалтинговые услуги в области управления и стратегии',
    tradeActivity: 'Поставщик услуг',
    country: 'Россия',
    region: 'Санкт-Петербург',
    city: 'Санкт-Петербург',
    name: 'Service Provider B',
  },
  {
    id: '3',
    logo: 'https://avatars.mds.yandex.net/i?id=0b8872628f8a5da597f4fe16698f580a_l-10150478-images-thumbs&n=13',
    description: 'Аутсорсинг бухгалтерских и юридических услуг',
    tradeActivity: 'Поставщик услуг',
    country: 'Россия',
    region: 'Новосибирская область',
    city: 'Новосибирск',
    name: 'Service Provider C',
  }
]

export default defineEventHandler(() => {
  // Simulate a slight delay to mimic real API behavior
  return new Promise<CompanyShort[]>((resolve) => {
    setTimeout(() => {
      resolve(serviceProviders)
    }, 300)
  })
})
