import { describe, expect, it } from 'vitest'
import {
	buildTransportCellLines,
	buildTransportCellTooltip,
	shortenOrgName,
} from './transportDocumentLabels'

describe('buildTransportCellLines §1.4', () => {
	it('пусто для null', () => {
		expect(buildTransportCellLines(null)).toEqual([])
	})

	it('legacy MVP expedition → одна строка', () => {
		const lines = buildTransportCellLines({
			number: 'TE-100',
			date: '2025-04-08T00:00:00',
			type: 'transport_expedition',
		})
		expect(lines).toHaveLength(1)
		expect(lines[0]).toContain('Договор экспедиции')
		expect(lines[0]).toContain('TE-100')
	})

	it('рамочный + заявка + перевозчик — одна кнопка', () => {
		const lines = buildTransportCellLines({
			number: '999',
			type: 'carriage_contract',
			carrier_name: 'Общество с ограниченной ответственностью «Перевозчик Тест»',
			documents: [
				{
					id: 4,
					type: 'carriage_contract',
					number: '999',
					date: '2025-04-08',
					carrier_name: 'Общество с ограниченной ответственностью «Перевозчик Тест»',
				},
				{
					id: 5,
					type: 'carriage_application',
					number: '1',
					date: '2025-04-08',
					parent_id: 4,
				},
			],
		})
		expect(lines).toHaveLength(1)
		expect(lines[0]).toContain('Договор перевозки')
		expect(lines[0]).toContain('999')
		expect(lines[0]).toContain('Заявка №')
		expect(lines[0]).toContain('ООО «Перевозчик Тест»')
		expect(lines[0]).toContain(' · ')
	})

	it('tooltip — многострочный полный текст', () => {
		const tip = buildTransportCellTooltip({
			documents: [
				{
					id: 4,
					type: 'carriage_contract',
					number: '999',
					date: '2025-04-08',
					carrier_name: 'ООО Перевозчик Тест',
				},
			],
			carrier_name: 'ООО Перевозчик Тест',
		})
		expect(tip).toContain('Договор перевозки')
		expect(tip).toContain('ООО Перевозчик Тест')
		expect(tip).toContain('\n')
	})

	it('shortenOrgName сокращает полное юрлицо', () => {
		expect(
			shortenOrgName('Общество с ограниченной ответственностью «Перевозчик Тест»'),
		).toBe('ООО «Перевозчик Тест»')
		expect(shortenOrgName('ООО Перевозчик Тест')).toBe('ООО Перевозчик Тест')
	})
})
