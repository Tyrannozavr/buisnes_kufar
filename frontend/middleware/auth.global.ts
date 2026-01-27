import { useUserStore } from '~/stores/user'

export default defineNuxtRouteMiddleware((to) => {
  // Ограничиваем всё, что под /profile (документы, редактор, сообщения, профиль компании и т.д.)
  if (!to.path.startsWith('/profile')) return

  // Если пользователь уже авторизован в сторе — пускаем
  const userStore = useUserStore()
  if (userStore.isAuthenticated) return

  // Минимальный серверный/клиентский чек: наличие access_token cookie.
  // (В идеале — верифицировать токен на бэкенде, но это уже отдельная задача.)
  const accessToken = useCookie<string | null>('access_token')
  if (accessToken.value) return

  return navigateTo({
    path: '/auth/login',
    query: { redirect: to.fullPath },
  })
})

