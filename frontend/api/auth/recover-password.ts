import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const { email } = await readBody(event)
  
  // Mock response - in real app this would send an actual email
  return {
    success: true,
    message: 'Код подтверждения отправлен на вашу почту'
  }
}) 