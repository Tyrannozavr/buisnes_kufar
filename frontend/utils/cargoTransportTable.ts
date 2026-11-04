import type { CargoData } from '~/types/transport'

export type CargoTransportTableRow = {
	label: string
	value: string
}

const contactLine = (value: unknown): string => {
	if (value == null || value === '') return ''
	if (typeof value === 'string') return value
	if (typeof value === 'object') {
		const o = value as Record<string, unknown>
		const parts = [
			o.name,
			o.full_name,
			o.fio,
			o.phone,
			o.position,
		]
			.map((x) => (x == null ? '' : String(x).trim()))
			.filter(Boolean)
		return parts.join(', ')
	}
	return String(value)
}

const asText = (value: unknown): string => {
	if (value == null || value === '') return ''
	return String(value)
}

/** кг → тн для бланка (ЛК хранит кг). */
export const kgToTonsLabel = (kg: unknown): string => {
	const n = Number(kg)
	if (!Number.isFinite(n) || n <= 0) return ''
	const tons = n / 1000
	return Number.isInteger(tons) ? String(tons) : tons.toFixed(3).replace(/\.?0+$/, '')
}

export function buildCargoTransportTableRows(
	cargo: CargoData | null | undefined,
	snapshot: Record<string, unknown> | null | undefined,
): CargoTransportTableRow[] {
	const vehicle = (snapshot?.vehicle ?? {}) as Record<string, unknown>
	const driver = (snapshot?.driver ?? {}) as Record<string, unknown>
	const c = cargo || {}

	const rate = c.rate != null && c.rate !== ('' as unknown) ? String(c.rate) : ''
	const payment = asText(c.payment_terms)
	const rateLine = [rate, payment].filter(Boolean).join(', ')

	return [
		{ label: 'Дата загрузки', value: asText(c.loading_date) },
		{ label: 'Дата разгрузки', value: asText(c.unloading_date) },
		{ label: 'Время загрузки', value: asText(c.loading_time) },
		{ label: 'Время выгрузки', value: asText(c.unloading_time) },
		{ label: 'Адрес загрузки', value: asText(c.loading_address) },
		{ label: 'Адрес выгрузки', value: asText(c.unloading_address) },
		{ label: 'Маршрут', value: asText(c.route) },
		{ label: 'Контактное лицо на загрузке', value: contactLine(c.contact_loading) },
		{ label: 'Контактное лицо на разгрузке', value: contactLine(c.contact_unloading) },
		{ label: 'Наименование груза', value: asText(c.cargo_name) },
		{ label: 'Условия перевозки', value: asText(c.transport_conditions) },
		{ label: 'Тоннаж, тн', value: kgToTonsLabel(c.gross_weight) },
		{ label: 'Количество мест', value: asText(c.places_count) },
		{ label: 'Объём', value: asText(c.volume) },
		{ label: 'Ставка за перевозку, условия оплаты', value: rateLine },
		{ label: 'Водитель (ФИО)', value: asText(driver.full_name) },
		{ label: 'Паспорт РФ', value: '' }, // в ЛК нет — оставляем пустым
		{ label: 'Контактный телефон', value: asText(driver.phone) },
		{ label: 'Марка тягача', value: asText(vehicle.name) },
		{ label: 'Гос. номер тягача', value: asText(vehicle.plate_number) },
		{ label: 'Номер п/п', value: asText(vehicle.trailer_plate_number) },
	]
}

export function rowsToSnapshot(
	rows: CargoTransportTableRow[],
): Record<string, string> {
	const out: Record<string, string> = {}
	for (const row of rows) out[row.label] = row.value
	return out
}
