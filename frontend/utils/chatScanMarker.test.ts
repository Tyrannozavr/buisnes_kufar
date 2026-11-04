import { describe, expect, it } from 'vitest'
import {
	buildChatScanMarker,
	extractChatScanRefs,
	stripChatScanMarkers,
} from './chatScanMarker'

describe('chatScanMarker', () => {
	it('build + extract roundtrip', () => {
		const marker = buildChatScanMarker(1, 42, 'внж.png')
		expect(marker).toContain('deal=1')
		expect(extractChatScanRefs(`текст ${marker}`)).toEqual([
			{ dealId: 1, documentId: 42, filename: 'внж.png' },
		])
	})

	it('strip markers from visible text', () => {
		const marker = buildChatScanMarker(2, 9, 'a.pdf')
		expect(stripChatScanMarkers(`Привет ${marker}`)).toBe('Привет')
	})

	it('caps to one scan ref per message', () => {
		const a = buildChatScanMarker(1, 1, 'a.png')
		const b = buildChatScanMarker(2, 2, 'b.png')
		expect(extractChatScanRefs(`${a}${b}`)).toHaveLength(1)
		expect(extractChatScanRefs(`${a}${b}`)[0].documentId).toBe(1)
	})
})
