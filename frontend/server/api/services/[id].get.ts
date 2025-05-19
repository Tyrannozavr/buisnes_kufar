import { defineEventHandler } from 'h3'
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
    isDeleted: false
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
    isDeleted: false
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
    isDeleted: false
  }
]

export default defineEventHandler(async (event) => {
  const id = event.context.params?.id
  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'Service ID is required'
    })
  }

  const service = services.find(s => s.id === id && !s.isHidden && !s.isDeleted)
  if (!service) {
    throw createError({
      statusCode: 404,
      message: 'Service not found'
    })
  }

  return service
}) 