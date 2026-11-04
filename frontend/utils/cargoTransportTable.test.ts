import { describe, expect, it } from 'vitest'
import { buildCargoTransportTableRows, kgToTonsLabel } from './cargoTransportTable'

describe('cargoTransportTable', () => {
	it('converts kg to tons', () => {
		expect(kgToTonsLabel(2000)).toBe('2')
		expect(kgToTonsLabel(1500)).toBe('1.5')
		expect(kgToTonsLabel(null)).toBe('')
	})

	it('maps cargo and transport snapshot', () => {
		const rows = buildCargoTransportTableRows(
			{
				cargo_name: 'Щебень',
				gross_weight: 10000,
				loading_address: 'Минск',
				rate: 500,
				payment_terms: 'по факту',
			},
			{
				driver: { full_name: 'Иванов', phone: '+375' },
				vehicle: { name: 'МАЗ', plate_number: '1234', trailer_plate_number: 'AB' },
			},
		)
		const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]))
		expect(byLabel['Наименование груза']).toBe('Щебень')
		expect(byLabel['Тоннаж, тн']).toBe('10')
		expect(byLabel['Ставка за перевозку, условия оплаты']).toBe('500, по факту')
		expect(byLabel['Водитель (ФИО)']).toBe('Иванов')
		expect(byLabel['Паспорт РФ']).toBe('')
		expect(byLabel['Номер п/п']).toBe('AB')
	})
})
