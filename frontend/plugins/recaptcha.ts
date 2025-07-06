export default defineNuxtPlugin(() => {
  return {
    provide: {
      recaptcha: {
        siteKey: '6LdJHHorAAAAAG2JB9CyOtRQbPJWrxbdRPy0dMHO', // Замените на ваш публичный ключ
        
        async execute(action: string = 'submit'): Promise<string> {
          return new Promise((resolve, reject) => {
            if (typeof window === 'undefined') {
              reject(new Error('reCAPTCHA is not available on server side'))
              return
            }

            // Проверяем, загружен ли reCAPTCHA
            if (typeof window.grecaptcha === 'undefined') {
              reject(new Error('reCAPTCHA not loaded'))
              return
            }

            try {
              window.grecaptcha.ready(() => {
                window.grecaptcha.execute(this.siteKey, { action })
                  .then((token: string) => {
                    resolve(token)
                  })
                  .catch((error: any) => {
                    reject(error)
                  })
              })
            } catch (error) {
              reject(error)
            }
          })
        }
      }
    }
  }
})

// Расширяем типы для window
declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void
      execute: (siteKey: string, options: { action: string }) => Promise<string>
    }
  }
} 