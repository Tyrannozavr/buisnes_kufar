import { describe, expect, it } from 'vitest'
import { formatGrossNetFromLines, formatOrderValue, linesWithWeights } from './orderCargoTotals'

describe('orderCargoTotals §5', () => {
	it('sums quantity × weights', () => {
		expect(
			formatGrossNetFromLines([
				{ quantity: 2, gross: 10, net: 8 },
				{ quantity: 1, gross: 5, net: 4 },
			]),
		).toBe('25 / 20')
	})

	it('treats missing weight as 0', () => {
		expect(formatGrossNetFromLines([{ quantity: 3 }])).toBe('0 / 0')
	})

	it('formats money', () => {
		expect(formatOrderValue(1234.5)).toMatch(/1.?234/)
	})

	it('maps items by slug/article', () => {
		const lines = linesWithWeights(
			[
				{ name: 'a', article: 'A1', slug: 'a1', quantity: 2, units: 'шт', price: 1, amount: 2 },
			],
			{ a1: { gross: 3, net: 2 } },
		)
		expect(formatGrossNetFromLines(lines)).toBe('6 / 4')
	})
})
