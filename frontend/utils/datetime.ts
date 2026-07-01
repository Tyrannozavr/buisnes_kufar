const MOSCOW_TZ = 'Europe/Moscow'

/** API отдаёт UTC без суффикса Z — трактуем как UTC. */
export function parseApiDateTime(dateString: string): Date {
	if (!dateString?.trim()) return new Date(NaN)
	const trimmed = dateString.trim()
	const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(trimmed)
	return new Date(hasTimezone ? trimmed : `${trimmed}Z`)
}

export function formatMoscowTime(dateString: string): string {
	const date = parseApiDateTime(dateString)
	if (Number.isNaN(date.getTime())) return ''
	return new Intl.DateTimeFormat('ru-RU', {
		timeZone: MOSCOW_TZ,
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
	}).format(date)
}

export function formatMoscowDateTime(dateString: string): string {
	const date = parseApiDateTime(dateString)
	if (Number.isNaN(date.getTime())) return ''
	return new Intl.DateTimeFormat('ru-RU', {
		timeZone: MOSCOW_TZ,
		day: '2-digit',
		month: '2-digit',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	}).format(date)
}

export function formatMoscowDate(dateString: string): string {
	const date = parseApiDateTime(dateString)
	if (Number.isNaN(date.getTime())) return 'Нет даты'
	return new Intl.DateTimeFormat('ru-RU', {
		timeZone: MOSCOW_TZ,
		day: '2-digit',
		month: '2-digit',
		year: 'numeric',
	}).format(date)
}
