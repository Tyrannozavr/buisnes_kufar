import { defineEventHandler, readBody } from 'h3'
import { mockMessages } from '~/server/mock/chatData'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { chatId, senderId, content } = body

  if (!chatId || !senderId || !content) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID, sender ID and content are required'
    })
  }

  // Create new message
  const newMessage = {
    id: `msg${Date.now()}`,
    sender: {
      id: senderId,
      name: 'Current Company', // In real implementation, get from user data
      logo: '/images/default-company-logo.png'
    },
    content,
    createdAt: new Date().toISOString(),
    isRead: false
  }

  // Add message to mock data
  if (!mockMessages[chatId]) {
    mockMessages[chatId] = []
  }
  mockMessages[chatId].push(newMessage)

  return newMessage
}) 