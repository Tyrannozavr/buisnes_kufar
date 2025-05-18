export default defineEventHandler((event) => {

    // Only return federal districts for Russia
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

})
