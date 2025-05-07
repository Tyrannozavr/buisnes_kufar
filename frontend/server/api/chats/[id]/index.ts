import { defineEventHandler } from 'h3'
import { mockChats } from '~/server/mock/chatData'

export default defineEventHandler(async (event) => {
  const id = event.context.params?.id

  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID is required'
    })
  }

  const chat = mockChats.find(c => c.id === id)

  if (!chat) {
    throw createError({
      statusCode: 404,
      message: 'Chat not found'
    })
  }

  return chat
}) 