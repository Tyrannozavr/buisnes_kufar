import type { Chat, ChatMessage } from '~/types/chat'

export const mockChats: Chat[] = [
  {
    id: '1',
    participants: [
      {
        id: 'company1',
        name: 'ООО "ТехноПром"',
        logo: 'https://rencaigroup.com/wp-content/uploads/2018/01/HR-Review-Internal-Team.jpg'
      },
      {
        id: 'company2',
        name: 'ИП Иванов',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      }
    ],
    lastMessage: {
      id: 'msg1',
      chatId: '1',
      sender: {
        id: 'company1',
        name: 'ООО "ТехноПром"',
        logo: 'https://rencaigroup.com/wp-content/uploads/2018/01/HR-Review-Internal-Team.jpg'
      },
      content: 'Добрый день! Интересует поставка оборудования',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '2',
    participants: [
      {
        id: 'company1',
        name: 'ООО "ТехноПром"',
        logo: 'https://rencaigroup.com/wp-content/uploads/2018/01/HR-Review-Internal-Team.jpg'
      },
      {
        id: 'company3',
        name: 'АО "СтройМаш"',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      }
    ],
    lastMessage: {
      id: 'msg2',
      chatId: '2',
      sender: {
        id: 'company3',
        name: 'АО "СтройМаш"',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      },
      content: 'Спасибо за предложение, мы рассмотрим его',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      updatedAt: new Date(Date.now() - 3600000).toISOString()
    },
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date(Date.now() - 3600000).toISOString()
  }
]

export const mockMessages: Record<string, ChatMessage[]> = {
  '1': [
    {
      id: 'msg1',
      chatId: '1',
      sender: {
        id: 'company1',
        name: 'ООО "ТехноПром"',
        logo: 'https://rencaigroup.com/wp-content/uploads/2018/01/HR-Review-Internal-Team.jpg'
      },
      content: 'Добрый день! Интересует поставка оборудования',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 'msg2',
      chatId: '1',
      sender: {
        id: 'company2',
        name: 'ИП Иванов',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      },
      content: 'Здравствуйте! Какое именно оборудование вас интересует?',
      createdAt: new Date(Date.now() - 1800000).toISOString(),
      updatedAt: new Date(Date.now() - 1800000).toISOString()
    },
    {
      id: 'msg3',
      chatId: '1',
      sender: {
        id: 'company1',
        name: 'ООО "ТехноПром"',
        logo: 'https://rencaigroup.com/wp-content/uploads/2018/01/HR-Review-Internal-Team.jpg'
      },
      content: 'Вот спецификация оборудования',
      file: {
        name: 'specification.pdf',
        url: '/files/specification.pdf',
        type: 'application/pdf',
        size: 1024576
      },
      createdAt: new Date(Date.now() - 900000).toISOString(),
      updatedAt: new Date(Date.now() - 900000).toISOString()
    }
  ],
  '2': [
    {
      id: 'msg3',
      chatId: '2',
      sender: {
        id: 'company3',
        name: 'АО "СтройМаш"',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      },
      content: 'Спасибо за предложение, мы рассмотрим его',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      updatedAt: new Date(Date.now() - 3600000).toISOString()
    }
  ]
} 