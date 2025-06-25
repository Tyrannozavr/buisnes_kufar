# Переиспользуемые компоненты для кнопок сообщений

## MessageButton

Компонент для отображения кнопки "Написать сообщение" с автоматическим скрытием для собственной компании.

### Props

- `companyId` (number, required) - ID компании
- `companyName` (string, optional) - Название компании для дополнительной проверки
- `variant` (string, optional) - Вариант кнопки: 'soft', 'ghost', 'solid' (по умолчанию: 'soft')
- `size` (string, optional) - Размер кнопки: 'sm', 'md', 'lg' (по умолчанию: 'sm')
- `showIcon` (boolean, optional) - Показывать ли иконку конверта (по умолчанию: true)
- `customText` (string, optional) - Кастомный текст кнопки (по умолчанию: 'Написать')

### Использование

```vue
<MessageButton
  :company-id="company.id"
  :company-name="company.name"
  variant="soft"
  size="sm"
  custom-text="Написать"
/>
```

## MessageButtonBySlug

Компонент для отображения кнопки "Написать сообщение" с использованием slug компании.

### Props

- `companySlug` (string, required) - Slug компании
- `companyName` (string, optional) - Название компании для дополнительной проверки
- `variant` (string, optional) - Вариант кнопки: 'soft', 'ghost', 'solid' (по умолчанию: 'soft')
- `size` (string, optional) - Размер кнопки: 'sm', 'md', 'lg' (по умолчанию: 'sm')
- `showIcon` (boolean, optional) - Показывать ли иконку конверта (по умолчанию: true)
- `customText` (string, optional) - Кастомный текст кнопки (по умолчанию: 'Написать')

### Использование

```vue
<MessageButtonBySlug
  :company-slug="company.slug"
  :company-name="company.name"
  variant="solid"
  size="md"
  custom-text="Написать сообщение"
/>
```

## Логика работы

Оба компонента автоматически:

1. Проверяют, аутентифицирован ли пользователь
2. Сравнивают ID/slug компании с данными пользователя
3. Скрывают кнопку, если пользователь смотрит на свою компанию
4. При клике перенаправляют в соответствующий чат

## Зависимости

- `useUserStore` - для получения данных пользователя
- `navigateToChatById` / `navigateToChatBySlug` - для навигации к чату
- `UButton` - базовый компонент кнопки 