import { describe, expect, it } from 'vitest'
import { tabFromRoute, tabFromQuery, HASH_TO_TAB } from './editorNavigation'

describe('tabFromRoute', () => {
	it('читает вкладку из hash', () => {
		expect(tabFromRoute('#contract')).toBe('5')
		expect(tabFromRoute('#bill')).toBe('1')
		expect(tabFromRoute('#order')).toBe('0')
	})

	it('читает order/bill из query', () => {
		expect(tabFromQuery('order')).toBe('0')
		expect(tabFromQuery('bill')).toBe('1')
		expect(tabFromQuery('other')).toBeNull()
	})

	it('hash побеждает при конфликте с ?tab=', () => {
		expect(tabFromRoute('#contract', 'order')).toBe('5')
		expect(tabFromRoute('#bill', 'order')).toBe('1')
		expect(tabFromRoute('#accompanyingDocuments', 'bill')).toBe('3')
	})

	it('hash побеждает, если query пустой', () => {
		expect(tabFromRoute('#contract', undefined)).toBe('5')
		expect(tabFromRoute('#contract', null)).toBe('5')
	})

	it('HASH_TO_TAB покрывает все вкладки редактора', () => {
		expect(HASH_TO_TAB['#order']).toBe('0')
		expect(HASH_TO_TAB['#othersDocument']).toBe('7')
	})
})
