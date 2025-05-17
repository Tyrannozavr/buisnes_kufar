export default defineEventHandler((event) => {
  const query = getQuery(event)
  const country = query.country as string

  // Only return federal districts for Russia
  if (country === 'Россия') {
    return [
      'Центральный',
      'Северо-Западный',
      'Южный',
      'Северо-Кавказский',
      'Приволжский',
      'Уральский',
      'Сибирский',
      'Дальневосточный'
    ].map(district => ({label: district, value: district}))
  }

  // Return empty array for other countries
  return []
})
