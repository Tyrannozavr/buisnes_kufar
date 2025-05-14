import { defineEventHandler, readBody } from 'h3'
import { mockChats, mockMessages } from '~/server/mock/chatData'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { participantId, participantName, participantLogo } = body

  if (!participantId || !participantName) {
    throw createError({
      statusCode: 400,
      message: 'Participant ID and name are required'
    })
  }

  // Create new chat
  const newChat = {
    id: `chat${Date.now()}`,
    participants: [
      {
        id: 'company1', // Current company ID
        name: 'ООО "ТехноПром"', // Current company name
        logo: 'https://rencaigroup.com/wp-content/uploads/2018/01/HR-Review-Internal-Team.jpg'
      },
      {
        id: participantId,
        name: participantName,
        logo: participantLogo || '/images/default-company-logo.png'
      }
    ],
    lastMessage: undefined,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }

  // Add chat to mock data
  mockChats.push(newChat)
  mockMessages[newChat.id] = []

  // Return the created chat
  return {
    id: newChat.id,
    participants: newChat.participants,
    lastMessage: null,
    createdAt: newChat.createdAt,
    updatedAt: newChat.updatedAt
  }
}) 