import type { Company, Product, Announcement, Message, Deal } from '~/types'

export const mockCompanies: Company[] = [
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
  }
]

export const mockProducts: Product[] = [
  {
    id: '1',
    companyId: '1',
    name: 'Промышленный станок ЧПУ',
    type: 'product',
    price: 1500000,
    images: ['/images/products/cnc-machine-1.jpg', '/images/products/cnc-machine-2.jpg'],
    characteristics: [
      { name: 'Мощность', value: '5 кВт' },
      { name: 'Рабочая зона', value: '1000x1000x500 мм' },
      { name: 'Точность', value: '0.01 мм' }
    ],
    isHidden: false,
    isDeleted: false
  },
  {
    id: '2',
    companyId: '2',
    name: 'Строительство коттеджа',
    type: 'service',
    price: 5000000,
    images: ['/images/services/cottage-1.jpg', '/images/services/cottage-2.jpg'],
    characteristics: [
      { name: 'Площадь', value: '150 м²' },
      { name: 'Сроки', value: '6 месяцев' },
      { name: 'Гарантия', value: '5 лет' }
    ],
    isHidden: false,
    isDeleted: false
  }
]

export const mockAnnouncements: Announcement[] = [
  {
    id: '1',
    companyId: '1',
    title: 'Новая линейка станков ЧПУ',
    content: 'Представляем новую линейку станков с ЧПУ с улучшенными характеристиками...',
    images: ['/images/announcements/cnc-new.jpg'],
    createdAt: '2024-04-20T10:00:00Z',
    isPublished: true,
    notifyPartners: true,
    notifySuppliers: false,
    notifyBuyers: true
  },
  {
    id: '2',
    companyId: '2',
    title: 'Специальное предложение на строительство',
    content: 'Действует специальное предложение на строительство коттеджей...',
    images: ['/images/announcements/cottage-special.jpg'],
    createdAt: '2024-04-19T15:30:00Z',
    isPublished: true,
    notifyPartners: true,
    notifySuppliers: false,
    notifyBuyers: true
  }
]

export const mockMessages: Message[] = [
  {
    id: '1',
    fromCompanyId: '1',
    toCompanyId: '2',
    subject: 'Запрос на сотрудничество',
    content: 'Здравствуйте! Заинтересованы в сотрудничестве...',
    createdAt: '2024-04-18T09:15:00Z',
    isRead: false
  }
]

export const mockDeals: Deal[] = [
  {
    id: '1',
    buyerId: '2',
    sellerId: '1',
    productId: '1',
    status: 'open',
    createdAt: '2024-04-17T14:20:00Z'
  }
] 