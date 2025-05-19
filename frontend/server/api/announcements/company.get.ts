import { defineEventHandler, getQuery } from 'h3'
import type { Announcement } from '~/types/announcement'

export const announcements: Announcement[] = [
  {
    id: '1',
    companyId: 1,
    companyName: 'ТехноПром',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Новая линейка станков ЧПУ',
    content: 'Представляем новую линейку станков с ЧПУ с улучшенными характеристиками. Наши инженеры разработали инновационную систему управления, которая повышает точность обработки на 30% и снижает энергопотребление. Станки уже доступны для заказа с доставкой по всей России.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-20T10:00:00Z',
    updatedAt: '2024-04-20T10:00:00Z',
    date: '2024-04-20',
    topic: 'Новинки',
    category: 'Товары',
    published: false,
    notifications: {
      partners: true,
      customers: true,
      suppliers: false,
      sent: false
    }
  },
  {
    id: '2',
    companyId: 2,
    companyName: 'СтройСервис',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Специальное предложение на строительство',
    content: 'Действует специальное предложение на строительство коттеджей. При заказе строительства до конца месяца, вы получаете проект ландшафтного дизайна в подарок. Наши специалисты используют только качественные материалы и современные технологии строительства.',
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
  },
  {
    id: '3',
    companyId: 3,
    companyName: 'ИнноТех',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Запуск новой системы автоматизации',
    content: 'Компания ИнноТех представляет новую систему автоматизации производственных процессов. Система позволяет сократить затраты на производство до 25% и увеличить производительность. Приглашаем на демонстрацию системы в нашем офисе.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-18T09:45:00Z',
    updatedAt: '2024-04-18T09:45:00Z',
    date: '2024-04-18',
    topic: 'Технологии',
    category: 'Товары',
    published: false,
    notifications: {
      partners: true,
      customers: true,
      suppliers: true,
      sent: false
    }
  },
  {
    id: '4',
    companyId: 1,
    companyName: 'ТехноПром',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Расширение производственных мощностей',
    content: 'ООО "ТехноПром" сообщает о расширении производственных мощностей. Мы открыли новый цех площадью 5000 кв.м., что позволит увеличить объем производства на 40%. Это позволит нам сократить сроки выполнения заказов и расширить ассортимент продукции.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-15T14:20:00Z',
    updatedAt: '2024-04-15T14:20:00Z',
    date: '2024-04-15',
    topic: 'Развитие',
    category: 'Партнерство',
    published: true,
    notifications: {
      partners: true,
      customers: false,
      suppliers: true,
      sent: true
    }
  },
  {
    id: '5',
    companyId: 2,
    companyName: 'СтройСервис',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Новые технологии в строительстве',
    content: 'СтройСервис внедряет новые технологии в строительстве. Мы начали использовать инновационные материалы, которые повышают энергоэффективность зданий и сокращают сроки строительства. Приглашаем посетить наш демонстрационный объект.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-12T11:10:00Z',
    updatedAt: '2024-04-12T11:10:00Z',
    date: '2024-04-12',
    topic: 'Инновации',
    category: 'Товары',
    published: true,
    notifications: {
      partners: false,
      customers: true,
      suppliers: false,
      sent: true
    }
  },
  {
    id: '6',
    companyId: 3,
    companyName: 'ИнноТех',
    companyLogo: 'https://www.svgrepo.com/show/152278/marketing.svg',
    title: 'Участие в международной выставке',
    content: 'ИнноТех примет участие в международной выставке электроники и автоматизации. Мы представим наши последние разработки и инновационные решения. Приглашаем посетить наш стенд №B42 в павильоне 3.',
    images: ['https://www.svgrepo.com/show/152278/marketing.svg'],
    createdAt: '2024-04-10T16:30:00Z',
    updatedAt: '2024-04-10T16:30:00Z',
    date: '2024-04-10',
    topic: 'События',
    category: 'События',
    published: false,
    notifications: {
      partners: true,
      customers: false,
      suppliers: false,
      sent: false
    }
  }
]

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const page = parseInt(query.page as string) || 1
  const perPage = parseInt(query.perPage as string) || 10

  // Calculate pagination
  const startIndex = (page - 1) * perPage
  const endIndex = startIndex + perPage
  const paginatedAnnouncements = announcements.slice(startIndex, endIndex)

  // Return paginated data with metadata
  return {
    data: paginatedAnnouncements,
    pagination: {
      total: announcements.length,
      page,
      perPage,
      totalPages: Math.ceil(announcements.length / perPage)
    }
  }
})