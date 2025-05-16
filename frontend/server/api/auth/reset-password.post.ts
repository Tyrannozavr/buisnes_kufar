import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const { email, code, newPassword } = await readBody(event)
  
  // Mock password reset - in real app this would update the password in database
  if (code === '123456') { // Mock code for testing
    return {
      success: true,
      message: 'Пароль успешно изменен'
    }
  }
  
  return {
    success: false,
    message: 'Неверный код подтверждения'
  }
}) 