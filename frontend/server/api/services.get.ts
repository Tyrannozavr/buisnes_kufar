import { defineEventHandler, getQuery } from 'h3'
import type { Service } from '~/types/service'

// Mock data for services
const services: Service[] = [
  {
    id: '1',
    companyId: '1',
    name: 'Проектирование промышленных объектов',
    description: 'Профессиональное проектирование промышленных зданий и сооружений. Включает разработку архитектурных, конструктивных и инженерных решений.',
    article: 'PROJ-100',
    type: 'Услуга',
    price: 1000000,
    images: [
      'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
    ],
    characteristics: [
      { name: 'Сроки', value: '3-6 месяцев' },
      { name: 'Площадь', value: 'до 10000 м²' },
      { name: 'Гарантия', value: '2 года' }
    ],
    isHidden: false,
    isDeleted: false,
    slug: 'proektirovanie-promyshlennyh-obektov'
  },
  {
    id: '2',
    companyId: '2',
    name: 'Монтаж промышленного оборудования',
    description: 'Установка и наладка промышленного оборудования любой сложности. Опытные специалисты обеспечат качественный монтаж и пусконаладку.',
    article: 'INST-200',
    type: 'Услуга',
    price: 800000,
    images: [
      'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
    ],
    characteristics: [
      { name: 'Сроки', value: '1-3 месяца' },
      { name: 'Тип оборудования', value: 'Любое' },
      { name: 'Гарантия', value: '1 год' }
    ],
    isHidden: false,
    isDeleted: false,
    slug: 'montazh-promyshlennogo-oborudovaniya'
  },
  {
    id: '3',
    companyId: '3',
    name: 'Техническое обслуживание',
    description: 'Регулярное техническое обслуживание промышленного оборудования. Предотвращение поломок и продление срока службы техники.',
    article: 'MAINT-300',
    type: 'Услуга',
    price: 500000,
    images: [
      'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
    ],
    characteristics: [
      { name: 'Периодичность', value: 'Ежемесячно' },
      { name: 'Тип оборудования', value: 'Любое' },
      { name: 'Гарантия', value: '1 год' }
    ],
    isHidden: false,
    isDeleted: false,
    slug: 'tehnicheskoe-obsluzhivanie'
  }
]

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const page = parseInt(query.page as string) || 1
  const perPage = parseInt(query.perPage as string) || 10
  const limit = parseInt(query.limit as string)

  // Filter out hidden and deleted services
  const filteredServices = services.filter(s => !s.isHidden && !s.isDeleted)

  // Apply limit if specified
  const limitedServices = limit ? filteredServices.slice(0, limit) : filteredServices

  // Calculate pagination
  const startIndex = (page - 1) * perPage
  const endIndex = startIndex + perPage
  const paginatedServices = limitedServices.slice(startIndex, endIndex)

  return {
    data: paginatedServices,
    pagination: {
      total: limitedServices.length,
      page,
      perPage,
      totalPages: Math.ceil(limitedServices.length / perPage)
    }
  }
})