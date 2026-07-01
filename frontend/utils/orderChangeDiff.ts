import type { DealOrderChangeDiff, OrderLineChange } from "~/types/dealResponse"
import type { ProductsInOrder } from "~/types/order"

export type OrderDisplayRow = ProductsInOrder & {
	changeStatus?: OrderLineChange["status"]
	changedFields?: string[]
	isRemovedRow?: boolean
}

export const productMatchKey = (product: Pick<ProductsInOrder, "article" | "name">): string => {
	const article = (product.article ?? "").trim()
	if (article) return `a:${article}`
	return `n:${(product.name ?? "").trim().toLowerCase()}`
}

export const findLineChange = (
	diff: DealOrderChangeDiff | null | undefined,
	product: Pick<ProductsInOrder, "article" | "name">,
): OrderLineChange | undefined => {
	if (!diff?.items?.length) return undefined
	const key = productMatchKey(product)
	return diff.items.find((item) => item.match_key === key)
}

export const buildOrderDisplayRows = (
	products: ProductsInOrder[],
	diff: DealOrderChangeDiff | null | undefined,
): OrderDisplayRow[] => {
	const rows: OrderDisplayRow[] = products.map((product) => {
		const line = findLineChange(diff, product)
		return {
			...product,
			changeStatus: line?.status,
			changedFields: line?.changed_fields ?? [],
		}
	})

	if (!diff?.items?.length) return rows

	for (const line of diff.items) {
		if (line.status !== "removed") continue
		rows.push({
			name: line.product_name ?? "",
			article: line.product_article ?? "",
			quantity: line.quantity ?? 0,
			units: line.unit_of_measurement ?? "",
			price: line.price ?? 0,
			amount: line.amount ?? 0,
			changeStatus: "removed",
			changedFields: [],
			isRemovedRow: true,
		})
	}

	return rows
}

export const orderCellHighlightClass = (
	row: OrderDisplayRow,
	field: string,
): string => {
	if (row.changeStatus === "added") return "order-change-added"
	if (row.changeStatus === "removed") return "order-change-removed"
	if (row.changeStatus === "modified" && row.changedFields?.includes(field)) {
		return "order-change-modified"
	}
	return ""
}

export const orderRowHighlightClass = (row: OrderDisplayRow): string => {
	if (row.changeStatus === "added") return "order-change-row-added"
	if (row.changeStatus === "removed") return "order-change-row-removed"
	return ""
}
