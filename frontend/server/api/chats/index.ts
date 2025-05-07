import { defineEventHandler, getQuery } from 'h3'
import { mockChats } from '~/server/mock/chatData'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const userId = query.userId as string

  if (!userId) {
    throw createError({
      statusCode: 400,
      message: 'User ID is required'
    })
  }

  // Filter chats where the user is a participant

  return mockChats
  // return mockChats.filter(chat =>
  //   chat.participants.some(p => p.id === userId)
  // )
}) 