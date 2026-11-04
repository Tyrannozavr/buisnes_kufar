import type { ProductItem } from '~/types/dealState'

/** Σ(кол-во × вес карточки); пустой вес = 0. Возвращает «брутто / нетто» в кг. */
export function formatGrossNetFromLines(
	lines: Array<{ quantity: number; gross?: number | null; net?: number | null }>,
): string {
	let gross = 0
	let net = 0
	for (const line of lines) {
		const qty = Number(line.quantity) || 0
		gross += qty * (Number(line.gross) || 0)
		net += qty * (Number(line.net) || 0)
	}
	const g = Number.isInteger(gross) ? String(gross) : gross.toFixed(3).replace(/\.?0+$/, '')
	const n = Number.isInteger(net) ? String(net) : net.toFixed(3).replace(/\.?0+$/, '')
	return `${g} / ${n}`
}

export function formatOrderValue(total: number | null | undefined): string {
	if (total == null || !Number.isFinite(Number(total))) return ''
	return Number(total).toLocaleString('ru-RU', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	})
}

export type WeightLookup = Record<string, { net?: number | null; gross?: number | null }>

/** Сопоставить позиции заказа с весами по article или slug. */
export function linesWithWeights(
	items: ProductItem[],
	byKey: WeightLookup,
): Array<{ quantity: number; gross?: number | null; net?: number | null }> {
	return items.map((item) => {
		const hit =
			(item.slug && byKey[item.slug]) ||
			(item.article && byKey[item.article]) ||
			null
		return {
			quantity: item.quantity,
			gross: hit?.gross ?? 0,
			net: hit?.net ?? 0,
		}
	})
}
