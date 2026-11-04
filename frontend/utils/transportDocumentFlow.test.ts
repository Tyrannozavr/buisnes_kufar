import { describe, expect, it } from 'vitest'
import { resolveTransportDocFlow } from './transportDocumentFlow'

describe('resolveTransportDocFlow §1.3', () => {
	it('без перевозчиков → alert и закрытие', () => {
		const step = resolveTransportDocFlow({
			docType: 'carriage_contract',
			carriersCount: 0,
			dealTransport: null,
		})
		expect(step.step).toBe('alert')
		if (step.step === 'alert') {
			expect(step.message).toContain('Перевозчики')
			expect(step.backTo).toBe('close')
		}
	})

	it('договор перевозки при наличии перевозчиков → пикер орг+договоры', () => {
		const step = resolveTransportDocFlow({
			docType: 'carriage_contract',
			carriersCount: 2,
			dealTransport: null,
		})
		expect(step).toEqual({
			step: 'org_contracts_picker',
			docType: 'carriage_contract',
			showContracts: true,
		})
	})

	it('договор-заявка → пикер без списка договоров', () => {
		const step = resolveTransportDocFlow({
			docType: 'carriage_order',
			carriersCount: 1,
			dealTransport: null,
		})
		expect(step).toEqual({
			step: 'org_contracts_picker',
			docType: 'carriage_order',
			showContracts: false,
		})
	})

	it('заявка без рамочного на заказе → alert назад к типам', () => {
		const step = resolveTransportDocFlow({
			docType: 'carriage_application',
			carriersCount: 1,
			dealTransport: { number: 'x', type: 'expedition_contract', documents: [] },
		})
		expect(step.step).toBe('alert')
		if (step.step === 'alert') {
			expect(step.message).toContain('нет выбранных Договоров на перевозку')
			expect(step.backTo).toBe('type_select')
		}
	})

	it('заявка при наличии рамочного → create_child', () => {
		const step = resolveTransportDocFlow({
			docType: 'carriage_application',
			carriersCount: 1,
			dealTransport: {
				documents: [
					{ id: 10, type: 'carriage_contract', number: '999', date: '2025-04-08' },
				],
			},
		})
		expect(step).toEqual({
			step: 'create_child',
			docType: 'carriage_application',
			parentId: 10,
			parentType: 'carriage_contract',
		})
	})

	it('поручение без договора экспедиции → alert', () => {
		const step = resolveTransportDocFlow({
			docType: 'forwarder_assignment',
			carriersCount: 1,
			dealTransport: {
				documents: [
					{ id: 1, type: 'carriage_contract', number: '1' },
				],
			},
		})
		expect(step.step).toBe('alert')
		if (step.step === 'alert') {
			expect(step.message).toContain('транспортной экспедиции')
		}
	})
})
