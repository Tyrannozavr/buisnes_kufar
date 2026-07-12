import { useDeals } from "~/composables/useDeals"
import { useChatsApi } from "~/api/chats"
import { buildEditorDealAbsoluteUrl } from "~/utils/editorNavigation"

export interface CounterpartData {
	companyId: number
	dealNumber: string
}

/**
 * Получает id компании и номер заказа контрагента
 * @param dealId - ID сделки
 * @param role - роль пользователя (buyer или seller)
 * @returns { companyId: number, dealNumber: string } | null
 */
export const getCounterpartData = (
	dealId: number,
	role: string
): CounterpartData | null => {
	if (!dealId || !role) return null

	const { findDeal } = useDeals()
	const deal = findDeal(dealId)
	if (!deal) return null

	if (role === "buyer") {
		const companyId = deal.seller?.companyId
		if (!companyId) return null
		return {
			companyId,
			dealNumber: deal.sellerOrderNumber ?? ""
		}
	}
	if (role === "seller") {
		const companyId = deal.buyer?.companyId
		if (!companyId) return null
		return {
			companyId,
			dealNumber: deal.buyerOrderNumber ?? ""
		}
	}
	return null
}

/**
 * Уведомление контрагента о загруженном скане документа (§2.6, §4.3 ТЗ).
 */
export const sendScanToCounterpart = async (
	dealId: number,
	role: "buyer" | "seller",
	counterpartData: CounterpartData,
	documentType: "order" | "bill" | "supply_contract",
	filename: string,
): Promise<void> => {
	if (!counterpartData?.companyId) return

	const { createChat, sendMessage } = useChatsApi()

	const orderNumber = String(await Promise.resolve(counterpartData.dealNumber ?? ""))
	const chatData = await createChat({
		participantId: counterpartData.companyId,
	})

	if (!chatData?.id) return

	const counterpartRole: "buyer" | "seller" = role === "buyer" ? "seller" : "buyer"
	const reviewUrl = buildEditorDealAbsoluteUrl(dealId, counterpartRole, documentType)

	const docLabel =
		documentType === "order"
			? "заказа"
			: documentType === "bill"
				? "счёта на оплату"
				: "договора поставки"
	const content = `Добавлен скан документа ${docLabel} ${orderNumber} (${filename}). Это не изменение условий заказа — только файл. [Открыть сканы](${reviewUrl})`

	await sendMessage(chatData.id, { content })
}

/**
 * Отправляет сообщение контрагенту о принятии/отклонении изменений или о внесенных изменениях
 * @param dealId - ID сделки
 * @param role - роль пользователя (buyer или seller)
 * @param counterpartData - данные о контрагенте
 * @param isConfirm - true/false - отправляем сообщение об принятии/отклонении изменений, undefined - отправляем сообщение об изменениях
 * @returns void
 */
export const sendMessageToCounterpart = async (
	dealId: number,
	role: "buyer" | "seller",
	counterpartData: CounterpartData,
	isConfirm?: boolean
): Promise<void> => {
	if (!counterpartData?.companyId) return

	const { createChat, sendMessage } = useChatsApi()

	const orderNumber = String(
		await Promise.resolve(counterpartData.dealNumber ?? "")
	)
	const chatData = await createChat({
		participantId: counterpartData.companyId
	})

	if (chatData?.id) {
		const counterpartRole: "buyer" | "seller" = role === "buyer" ? "seller" : "buyer"
		const reviewUrl = buildEditorDealAbsoluteUrl(dealId, counterpartRole, "order")
		const normalizedReviewUrl = isConfirm === undefined
			? `${reviewUrl}&confirmation=true`
			: reviewUrl

		let content = ""
		if (isConfirm === true) {
			content = `Изменения заказа ${orderNumber} ПРИНЯТЫ. [Просмотр заказа](${normalizedReviewUrl})`
		} else if (isConfirm === false) {
			content = `Изменения заказа ${orderNumber} ОТКЛОНЕНЫ. [Просмотр заказа](${normalizedReviewUrl})`
		} else {
			content = `Контрагент изменил данные заказа ${orderNumber}. [Просмотр заказа](${normalizedReviewUrl})`
		}

		await sendMessage(chatData.id, {
			content: content
		})
	}
}
