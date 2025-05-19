import { defineEventHandler } from 'h3'
import { mockMessages } from '~/server/mock/chatData'

export default defineEventHandler(async (event) => {
  const chatId = event.context.params?.id as string

  if (!chatId) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID is required'
    })
  }

  const messages = mockMessages[chatId] || []
  
  // Filter messages that have files and map them to a more convenient format
  const files = messages
    .filter(message => message.file)
    .map(message => ({
      id: message.file?.name + '-' + message.id, // Unique ID for each file
      name: message.file?.name,
      url: message.file?.url,
      type: message.file?.type,
      size: message.file?.size,
      messageId: message.id,
      sender: {
        id: message.sender.id,
        name: message.sender.name,
        logo: message.sender.logo
      },
      createdAt: message.createdAt
    }))
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()) // Sort by date, newest first
  
  return files
}) 