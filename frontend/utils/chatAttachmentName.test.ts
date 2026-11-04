import { describe, expect, it } from 'vitest'
import { chatAttachmentDisplayName, isStorageFileName } from './chatAttachmentName'

describe('chatAttachmentDisplayName', () => {
	it('detects storage uuid names', () => {
		expect(isStorageFileName('a3dca4ca3dc942d8b2cd616e2b9dd63f.png')).toBe(true)
		expect(isStorageFileName('договор скан.png')).toBe(false)
	})

	it('prefers human name from marker over uuid file_name', () => {
		expect(
			chatAttachmentDisplayName({
				file_name: 'a3dca4ca3dc942d8b2cd616e2b9dd63f.png',
				content: 'текст [[scan:deal=1;doc=2;name=договор внж.png]]',
			}),
		).toBe('договор внж.png')
	})

	it('uses file_name when it is already human', () => {
		expect(
			chatAttachmentDisplayName({
				file_name: 'scan-signed.pdf',
				content: '',
			}),
		).toBe('scan-signed.pdf')
	})
})
