export default defineEventHandler(() => {
  return [
    'Азербайджан',
    'Армения',
    'Беларусь',
    'Казахстан',
    'Кыргызстан',
    'Молдова',
    'Россия',
    'Таджикистан',
    'Узбекистан'
  ].map(country => ({label: country, value: country}))
})
