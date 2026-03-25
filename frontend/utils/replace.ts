import type { BillData } from '~/types/bill';

/**
 * @param line: string
 * @param billData: BillData
 * @returns string
 * @description replace fields in line with bill data
 * @example "{{ НОМЕР_СЧЕТА }}" -> "1234567890"
 * @example "{{ ДАТА }}" -> "01.01.2026"
 * @example "{{ СРОК_ОПЛАТЫ }}" -> "10"
 * @example "{{ СРОК_ПОСТАВКИ }}" -> "10"
 */
export const replaceFields = (line: string, billData: BillData): string => {
	return line.replaceAll('{{ НОМЕР_СЧЕТА }}', billData.number)
		.replaceAll('{{ ДАТА }}', normalizeDate(billData.date))
		.replaceAll('{{ СРОК_ОПЛАТЫ_СЧЕТА_ДОГОВОРА }}', billData.paymentTermsContract)
		.replaceAll('{{ СРОК_ОПЛАТЫ_СЧЕТА_ОФЕРТА }}', billData.paymentTermsOffer)
		.replaceAll('{{ СРОК_ПОСТАВКИ_СЧЕТА_ДОГОВОРА }}', billData.deliveryTermsContract)
		.replaceAll('{{ НАЗВАНИЕ_КОМПАНИИ_ПОСТАВЩИКА }}', billData.seller.companyName ?? '');
}