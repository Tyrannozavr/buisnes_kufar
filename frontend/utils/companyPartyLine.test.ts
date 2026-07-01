import { describe, expect, it } from 'vitest'
import {
	formatCompanyPartyLine,
	formatCompanyRecipientLine,
	formatLegalAddressForParty,
	stripLeadingOrgType,
} from '~/utils/companyPartyLine'

describe('companyPartyLine', () => {
	it('stripLeadingOrgType removes duplicate org prefix', () => {
		expect(stripLeadingOrgType('ООО Поставщик Тест', 'ООО')).toBe('Поставщик Тест')
	})

	it('formatLegalAddressForParty avoids duplicate index', () => {
		expect(formatLegalAddressForParty('101000', '101000, г. Москва, ул. 1')).toBe(
			'101000, г. Москва, ул. 1',
		)
	})

	it('formatCompanyPartyLine builds TZ line without duplicates', () => {
		expect(
			formatCompanyPartyLine({
				companyType: 'ООО',
				companyName: 'ООО Поставщик Тест',
				inn: '7707083893',
				kpp: '770701001',
				index: '101000',
				legalAddress: '101000, г. Москва, ул. Поставщика, д. 1',
			}),
		).toBe(
			'ООО Поставщик Тест, 7707083893, 770701001, 101000, г. Москва, ул. Поставщика, д. 1',
		)
	})

	it('formatCompanyRecipientLine', () => {
		expect(
			formatCompanyRecipientLine({ companyType: 'ООО', companyName: 'ООО Поставщик Тест' }),
		).toBe('ООО Поставщик Тест')
	})
})
