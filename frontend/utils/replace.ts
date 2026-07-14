import type { BillData } from "~/types/bill"

export type ReplaceFieldsMode = "bill" | "bill-contract" | "bill-offer"

/** Любой остаточный {{ … }} — в бланке/DOC быть не должен */
const ANY_PLACEHOLDER_RE = /\{\{\s*[^}]+\s*\}\}/g

const placeholder = (name: string) =>
	new RegExp(`\\{\\{\\s*${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*\\}\\}`, "g")

/**
 * Подставить значения и гарантированно убрать служебные {{ ПОЛЕ }}.
 * Нет данных → пустая строка (не «{{ ДАТА }}»).
 */
export const replaceFields = (
	line: string,
	billData: BillData,
	mode: ReplaceFieldsMode = "bill",
): string => {
	const paymentTerms =
		mode === "bill-offer"
			? String(billData.paymentTermsOffer ?? "")
			: mode === "bill-contract"
				? String(billData.paymentTermsContract ?? "")
				: String(
						billData.paymentTerms ||
							billData.paymentTermsContract ||
							billData.paymentTermsOffer ||
							"",
					)

	const deliveryTerms = String(billData.deliveryTermsContract ?? "")
	const productionAddress = (billData.seller.productionAddress ?? "").trim()
	const number = String(billData.number ?? "")
	const date = normalizeDate(billData.date) || ""

	let out = line
		.replace(placeholder("НОМЕР_СЧЕТА"), number)
		.replace(placeholder("ДАТА"), date)
		.replace(placeholder("СРОК_ОПЛАТЫ"), paymentTerms)
		.replace(placeholder("СРОК_ПОСТАВКИ"), deliveryTerms)
		.replace(placeholder("СРОК_ОПЛАТЫ_СЧЕТА_ДОГОВОРА"), String(billData.paymentTermsContract ?? ""))
		.replace(placeholder("СРОК_ОПЛАТЫ_СЧЕТА_ОФЕРТЫ"), String(billData.paymentTermsOffer ?? ""))
		.replace(placeholder("СРОК_ПОСТАВКИ_СЧЕТА_ДОГОВОРА"), deliveryTerms)
		.replace(placeholder("НАЗВАНИЕ_КОМПАНИИ_ПОСТАВЩИКА"), billData.seller.companyName ?? "")
		.replace(placeholder("АДРЕС_ПРОИЗВОДСТВА_ПОСТАВЩИКА"), productionAddress)

	// На всякий случай — неизвестные / битые {{ … }} тоже стираем
	return out.replace(ANY_PLACEHOLDER_RE, "")
}

const PAYMENT_PLACEHOLDER_RE = /\{\{\s*СРОК_ОПЛАТЫ/
const DELIVERY_PLACEHOLDER_RE = /\{\{\s*СРОК_ПОСТАВКИ/

/**
 * Прячет строки условий с плейсхолдерами сроков, если соответствующая галка снята,
 * и перенумеровывает оставшиеся пункты (1. … 2. …), чтобы не было 3 → 5.
 */
export const filterTermsLinesByChecks = (
	text: string,
	opts: { includePayment: boolean; includeDelivery?: boolean },
): string[] => {
	const includeDelivery = opts.includeDelivery ?? true
	const filtered = text.split("\n").filter((line) => {
		if (!line.trim()) return true
		if (PAYMENT_PLACEHOLDER_RE.test(line) && !opts.includePayment) return false
		if (DELIVERY_PLACEHOLDER_RE.test(line) && !includeDelivery) return false
		return true
	})

	let conditionNo = 0
	return filtered.map((line) => {
		// «1.» / «1)» в начале строки (после пробелов) — пункт списка
		if (!/^\s*\d+[.)]/.test(line)) return line
		conditionNo += 1
		return line.replace(/^(\s*)\d+([.)])/, `$1${conditionNo}$2`)
	})
}
