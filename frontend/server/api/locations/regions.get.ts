export default defineEventHandler((event) => {
  const query = getQuery(event)
  const country = query.country as string
  const federalDistrict = query.federalDistrict as string

  // Default regions (will be returned if no country or federal district is selected)
  const defaultRegions = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирская область",
    "Екатеринбург",
    "Нижний Новгород",
    "Казань",
    "Челябинск",
    "Омск",
    "Самара",
    "Ростов-на-Дону",
    "Уфа",
    "Красноярск",
    "Воронеж",
    "Пермь",
    "Волгоград"
  ]

  // If no country is selected, return default regions
  if (!country) {
    return defaultRegions.map(region => ({label: region, value: region}))
  }

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
    // If no federal district is selected, return default regions
    if (!federalDistrict) {
      return defaultRegions.map(region => ({label: region, value: region}))
    }

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
  return [
      "Какой то регион по умолчанию",
      "Еще один регион по умолчанию",
  ]
})