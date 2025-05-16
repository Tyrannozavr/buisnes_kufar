import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const { email, code } = await readBody(event)
  
  // Mock email change - in real app this would update email in database
  if (code === '123456') { // Mock code for testing
    return {
      success: true,
      message: 'Email успешно изменен'
    }
  }
  
  return {
    success: false,
    message: 'Неверный код подтверждения'
  }
}) 