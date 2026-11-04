import { describe, expect, it } from 'vitest'
import {
	DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS,
	emptyCarriageOrderPayload,
} from './carriageOrderDefaults'
import { DEFAULT_EXPEDITION_CONTRACT_BODY } from './expeditionContractDefaults'
import { TRANSPORT_DOCUMENT_SHORT_LABELS } from '../types/transportDocument'

describe('stage 4 defaults', () => {
	it('order extra terms include 7 sample clauses', () => {
		expect(DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS).toContain('<ol>')
		expect(DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS.match(/<li>/g)?.length).toBe(7)
		const empty = emptyCarriageOrderPayload()
		expect(empty.extraTermsHtml).toBe(DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS)
	})

	it('expedition body mentions Клиент and Экспедитор', () => {
		expect(DEFAULT_EXPEDITION_CONTRACT_BODY).toMatch(/Клиент/)
		expect(DEFAULT_EXPEDITION_CONTRACT_BODY).toMatch(/Экспедитор/)
	})

	it('sales cell label for expedition is full title', () => {
		expect(TRANSPORT_DOCUMENT_SHORT_LABELS.expedition_contract).toBe(
			'Договор транспортной экспедиции',
		)
	})
})
