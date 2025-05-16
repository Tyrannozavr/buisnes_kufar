import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  console.log('Received verification request:', body)
  
  const { email, code } = body
  
  // Mock verification - in real app this would verify against stored code
  if (code === '123456') { // Mock code for testing
    console.log('Code verified successfully')
    return {
      success: true,
      message: 'Код подтвержден'
    }
  }
  
  console.log('Invalid code received')
  return {
    success: false,
    message: 'Неверный код подтверждения'
  }
}) 