import type { Announcement } from '~/types/announcement'

export const announcements: Announcement[] = [
  {
    id: '1',
    companyId: 1,
    companyName: 'ТехноПром',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Новое поступление оборудования',
    content: 'Компания ТехноПром рада сообщить о поступлении нового оборудования для производства. В наличии имеются станки последнего поколения с ЧПУ, а также вспомогательное оборудование.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-20T10:00:00Z',
    updatedAt: '2024-04-20T10:00:00Z',
    date: '2024-04-20',
    topic: 'Оборудование',
    category: 'Товары',
    published: true,
    notifications: {
      partners: true,
      customers: true,
      suppliers: false,
      sent: true
    }
  },
  {
    id: '2',
    companyId: 2,
    companyName: 'СтройСервис',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Специальное предложение на строительство',
    content: 'Действует специальное предложение на строительство коттеджей. При заказе строительства до конца месяца, вы получаете проект ландшафтного дизайна в подарок.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-19T15:30:00Z',
    updatedAt: '2024-04-19T15:30:00Z',
    date: '2024-04-19',
    topic: 'Акции',
    category: 'Акции',
    published: true,
    notifications: {
      partners: false,
      customers: true,
      suppliers: false,
      sent: true
    }
  }
]

export default defineEventHandler(() => {
  return {
    data: announcements,
    pagination: {
      total: announcements.length,
      page: 1,
      perPage: 5,
      totalPages: 1
    }
  }
}) 