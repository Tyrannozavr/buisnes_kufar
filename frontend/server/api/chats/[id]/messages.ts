import { defineEventHandler, getQuery } from 'h3'
import { mockMessages } from '~/server/mock/chatData'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const chatId = event.context.params?.id as string
  const page = parseInt(query.page as string) || 1
  const limit = parseInt(query.limit as string) || 50

  if (!chatId) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID is required'
    })
  }

  const messages = mockMessages[chatId] || []
  
  // Simulate pagination
  const start = (page - 1) * limit
  const end = start + limit
  
  return messages.slice(start, end)
}) 