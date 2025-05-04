export default defineEventHandler((event) => {
  const query = getQuery(event)
  const country = query.country as string
  const federalDistrict = query.federalDistrict as string
  
  // In a real application, you would filter regions based on country and federal district
  // For now, we'll return a static list
  
  // Kazakhstan regions
  if (country === 'Казахстан') {
    return [
      "Алматы",
      "Астана",
      "Балаканы",
      "Костанай",
      "Кызылорда",
      "Мангистау",
      "Акмолинская область",
      "Актюбинская область",
      "Алматинская область",
      "Атырауская область",
      "Восточно-Казахстанская область",
      "Жамбылская область",
      "Западно-Казахстанская область",
      "Карагандинская область",
      "Павлодарская область",
      "Северо-Казахстанская область",
      "Туркестанская область"
    ].map(region => ({label: region, value: region}))
  }
  
  // Russian regions based on federal district
  if (country === 'Россия') {
    if (federalDistrict === 'Центральный') {
      return [
        "Белгородская область",
        "Брянская область",
        "Владимирская область",
        "Воронежская область",
        "Ивановская область",
        "Калужская область",
        "Костромская область",
        "Курская область",
        "Липецкая область",
        "Москва",
        "Московская область",
        "Орловская область",
        "Рязанская область",
        "Смоленская область",
        "Тамбовская область",
        "Тверская область",
        "Тульская область",
        "Ярославская область"
      ].map(region => ({label: region, value: region}))
    }
    
    if (federalDistrict === 'Северо-Западный') {
      return [
        "Архангельская область",
        "Вологодская область",
        "Калининградская область",
        "Карелия",
        "Коми",
        "Ленинградская область",
        "Мурманская область",
        "Ненецкий автономный округ",
        "Новгородская область",
        "Псковская область",
        "Санкт-Петербург"
      ].map(region => ({label: region, value: region}))
    }
    
    // Add other federal districts as needed
  }
  
  // Default empty list if no match
  return []
})