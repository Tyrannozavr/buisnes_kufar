<template>
  <footer class="bg-gray-50 border-t">
    <UContainer>
      <div class="py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- О компании -->
          <div>
            <h3 class="font-semibold mb-4">О компании</h3>
            <p class="text-sm text-gray-600 mb-4">
              Строительный портал - ваш надежный партнер в мире строительства и ремонта. Мы помогаем найти качественные материалы и профессиональные услуги.
            </p>
          </div>

          <!-- Каталог -->
          <div>
            <h3 class="font-semibold mb-4">Каталог</h3>
            <ul class="space-y-2">
              <li>
                <NuxtLink to="/catalog/products" class="text-sm text-gray-600 hover:text-gray-900">
                  Товары
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/catalog/services" class="text-sm text-gray-600 hover:text-gray-900">
                  Услуги
                </NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Информация -->
          <div>
            <h3 class="font-semibold mb-4">Информация</h3>
            <ul class="space-y-2">
              <li>
                <NuxtLink to="/sitemap" class="text-sm text-gray-600 hover:text-gray-900">
                  Карта сайта
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/terms" class="text-sm text-gray-600 hover:text-gray-900">
                  Условия использования
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/privacy" class="text-sm text-gray-600 hover:text-gray-900">
                  Политика конфиденциальности
                </NuxtLink>
              </li>
            </ul>
          </div>

          <!-- Контакты -->
          <div>
            <h3 class="font-semibold mb-4">Контакты</h3>
            <ul class="space-y-2">
              <li class="text-sm text-gray-600">
                Email: info@example.com
              </li>
              <li class="text-sm text-gray-600">
                Телефон: +7 (999) 123-45-67
              </li>
              <li class="text-sm text-gray-600">
                Адрес: г. Москва, ул. Примерная, д. 1
              </li>
            </ul>
          </div>
        </div>

        <!-- Cookie Notice -->
        <div class="mt-8 pt-8 border-t">
          <p class="text-sm text-gray-600">
            Мы используем файлы cookie для улучшения работы сайта и предоставления персонализированного опыта. 
            Продолжая использовать наш сайт, вы соглашаетесь с использованием файлов cookie.
          </p>
        </div>

        <!-- Copyright -->
        <div class="mt-8 pt-8 border-t">
          <p class="text-sm text-gray-600">
            © {{ new Date().getFullYear() }} Строительный портал. Все права защищены.
          </p>
        </div>
      </div>
    </UContainer>
  </footer>
</template> 