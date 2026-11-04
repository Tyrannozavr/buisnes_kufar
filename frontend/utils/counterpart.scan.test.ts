import { describe, expect, it } from 'vitest'

/**
 * Логика подписей/вкладки для sendScanToCounterpart (§3.0) —
 * дублируем чистые ветки без Nuxt-зависимостей.
 */
type ScanDocumentType =
	| 'order'
	| 'bill'
	| 'bill_contract'
	| 'bill_offer'
	| 'supply_contract'
	| 'contract'

const scanDocLabel = (documentType: ScanDocumentType): string => {
	switch (documentType) {
		case 'order':
			return 'заказа'
		case 'bill':
			return 'счёта на оплату'
		case 'bill_contract':
			return 'счёта-договора'
		case 'bill_offer':
			return 'счёта-оферты'
		case 'supply_contract':
			return 'договора поставки'
		case 'contract':
			return 'договора перевозки'
		default:
			return 'документа'
	}
}

const scanEditorTab = (documentType: ScanDocumentType) => {
	if (documentType === 'order') return 'order'
	if (documentType === 'supply_contract') return 'supply_contract'
	if (documentType === 'contract') return 'contract'
	return 'bill'
}

describe('scan chat notify (§3.0)', () => {
	it('contract → подпись договора перевозки и вкладка contract', () => {
		expect(scanDocLabel('contract')).toBe('договора перевозки')
		expect(scanEditorTab('contract')).toBe('contract')
	})

	it('supply_contract не путается с contract', () => {
		expect(scanDocLabel('supply_contract')).toBe('договора поставки')
		expect(scanEditorTab('supply_contract')).toBe('supply_contract')
	})
})
