import { useDeals } from "~/composables/useDeals"
import { useChatsApi } from "~/api/chats"
import { buildEditorDealAbsoluteUrl, type EditorDocumentTab } from "~/utils/editorNavigation"
import { buildChatScanMarker } from "~/utils/chatScanMarker"

export interface CounterpartData {
	companyId: number
	dealNumber: string
}

export type ScanDocumentType =
	| "order"
	| "bill"
	| "bill_contract"
	| "bill_offer"
	| "supply_contract"
	| "contract"
	| "carriage_application"

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

const scanDocLabel = (documentType: ScanDocumentType): string => {
	switch (documentType) {
		case "order":
			return "заказа"
		case "bill":
			return "счёта на оплату"
		case "bill_contract":
			return "счёта-договора"
		case "bill_offer":
			return "счёта-оферты"
		case "supply_contract":
			return "договора поставки"
		case "contract":
			return "договора перевозки"
		case "carriage_application":
			return "заявки к договору перевозки"
		default:
			return "документа"
	}
}

const scanEditorTab = (documentType: ScanDocumentType): EditorDocumentTab => {
	if (documentType === "order") return "order"
	if (documentType === "supply_contract") return "supply_contract"
	if (documentType === "contract" || documentType === "carriage_application") {
		return "contract"
	}
	return "bill"
}

/**
 * Уведомление контрагента о скане (§2.6 / §3.0).
 * Сообщение уходит сразу (текст + маркер для мгновенного превью).
 * Копия в chat_files — фоном на бэке (если удалят скан сделки, вложение в чате останется).
 */
export const sendScanToCounterpart = async (
	dealId: number,
	role: "buyer" | "seller",
	counterpartData: CounterpartData,
	documentType: ScanDocumentType,
	filename: string,
	documentId?: number | null,
): Promise<number | null> => {
	if (!counterpartData?.companyId) return null

	const { createChat, sendMessage } = useChatsApi()

	const orderNumber = String(await Promise.resolve(counterpartData.dealNumber ?? ""))
	const chatData = await createChat({
		participantId: counterpartData.companyId,
	})

	if (!chatData?.id) return null

	const counterpartRole: "buyer" | "seller" = role === "buyer" ? "seller" : "buyer"
	const chatDocumentTab = scanEditorTab(documentType)
	const reviewUrl = buildEditorDealAbsoluteUrl(dealId, counterpartRole, chatDocumentTab)

	const docLabel = scanDocLabel(documentType)
	const hasDoc = Boolean(documentId && documentId > 0)
	const marker = hasDoc
		? `\n${buildChatScanMarker(dealId, documentId!, filename)}`
		: ""
	const content = `Добавлен скан документа ${docLabel} ${orderNumber} (${filename}). Это не изменение условий заказа — только файл. [Открыть сканы](${reviewUrl})${marker}`

	await sendMessage(chatData.id, {
		content,
		...(hasDoc
			? {
					attachDealId: dealId,
					attachDocumentId: documentId!,
					attachFileName: filename,
				}
			: {}),
	})
	return chatData.id
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

	if (!chatData?.id) {
		throw new Error("Не удалось создать или найти чат с контрагентом")
	}

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
