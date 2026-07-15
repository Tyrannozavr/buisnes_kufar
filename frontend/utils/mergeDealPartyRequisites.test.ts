import { describe, expect, it } from 'vitest'
import { mergeDealPartyRequisites } from '~/composables/useCompanyBillRequisites'
import type { Company as DealCompany } from '~/types/dealState'

describe('mergeDealPartyRequisites §7.4', () => {
	it('не затирает заполненные поля сделки пустыми значениями из ЛК', () => {
		const current: DealCompany = {
			companyName: 'ООО Сделка',
			inn: 123,
			legalAddress: 'ул. Сделки, 1',
		}
		const fresh: DealCompany = {
			companyName: '',
			inn: undefined,
			kpp: '770101001',
		}
		const merged = mergeDealPartyRequisites(current, fresh)
		expect(merged.companyName).toBe('ООО Сделка')
		expect(merged.inn).toBe(123)
		expect(merged.kpp).toBe('770101001')
	})
})
