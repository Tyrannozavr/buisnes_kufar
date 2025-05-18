export default defineEventHandler((event) => {
    const query = getQuery(event)
    const country = query.country as string

    if (country === 'Россия') {
        return [
            { label: 'Москва', value: 'Москва' },
            { label: 'Санкт-Петербург', value: 'Санкт-Петербург' },
            { label: 'Новосибирск', value: 'Новосибирск' },
            { label: 'Екатеринбург', value: 'Екатеринбург' },
            { label: 'Казань', value: 'Казань' }
        ]
    }

    // Default list of cities for other countries
    return [
        { label: 'Минск', value: 'Минск' },
        { label: 'Алматы', value: 'Алматы' },
        { label: 'Бишкек', value: 'Бишкек' },
        { label: 'Ереван', value: 'Ереван' },
        { label: 'Баку', value: 'Баку' }
    ]
})