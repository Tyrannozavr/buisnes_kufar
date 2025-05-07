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
      senderId: 'company1',
      content: 'Добрый день! Интересует поставка оборудования',
      createdAt: new Date().toISOString(),
      isRead: false
    },
    unreadCount: 1,
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
      senderId: 'company3',
      content: 'Спасибо за предложение, мы рассмотрим его',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      isRead: true
    },
    unreadCount: 0,
    updatedAt: new Date(Date.now() - 3600000).toISOString()
  }
]

export const mockMessages: Record<string, ChatMessage[]> = {
  '1': [
    {
      id: 'msg1',
      sender: {
        id: 'company1',
        name: 'ООО "ТехноПром"',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      },
      content: 'Добрый день! Интересует поставка оборудования',
      createdAt: new Date().toISOString(),
      isRead: false
    },
    {
      id: 'msg2',
      sender: {
        id: 'company2',
        name: 'ИП Иванов',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      },
      content: 'Здравствуйте! Какое именно оборудование вас интересует?',
      createdAt: new Date(Date.now() - 1800000).toISOString(),
      isRead: true
    }
  ],
  '2': [
    {
      id: 'msg3',
      sender: {
        id: 'company3',
        name: 'АО "СтройМаш"',
        logo: 'https://images.news18.com/ibnlive/uploads/2022/01/economic-survey-2021-164364536616x9.png'
      },
      content: 'Спасибо за предложение, мы рассмотрим его',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      isRead: true
    }
  ]
} 