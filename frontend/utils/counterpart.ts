import { usePurchasesStore } from "~/stores/purchases";
import { useSalesStore } from "~/stores/sales";
import { useChatsApi } from "~/api/chats";
import { useRouter } from "vue-router";

export interface CounterpartData {
  companyId: number;
  dealNumber: string;
}

/**
 * Получает id компании и номер заказа контрагента
 * @param dealId - ID сделки
 * @param role - роль пользователя (buyer или seller)
 * @returns { companyId: number, dealNumber: string } | null
 */
export const getCounterpartData = (
  dealId: number,
  role: string,
): CounterpartData | null => {
  if (!dealId || !role) return null;

	const purchasesStore = usePurchasesStore();
	const salesStore = useSalesStore();

  if (role === "buyer") {
    const deal = purchasesStore.findGoodsDeal(dealId);
    return {
      companyId: deal?.seller?.companyId ?? 0,
      dealNumber: deal?.sellerOrderNumber ?? "",
    };
  }
  if (role === "seller") {
    const deal = salesStore.findGoodsDeal(dealId);
    return {
      companyId: deal?.buyer?.companyId ?? 0,
      dealNumber: deal?.buyerOrderNumber ?? "",
    };
  }
  return null;
};


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
  role: 'buyer' | 'seller',
  counterpartData: CounterpartData,
  isConfirm?: boolean,
): Promise<void> => {
  if (!counterpartData) return;

	const { createChat, sendMessage } = useChatsApi();
	const router = useRouter();
	const route = useRoute();

	const orderNumber = String(
		await Promise.resolve(counterpartData.dealNumber ?? ""),
	);
	const chatData = await createChat({
		participantId: counterpartData.companyId,
	});

	if (chatData?.id) {
		const resolvedDealRoute = router.resolve({
			path: route.path,
			query: {
				dealId: dealId,
				role: role,
				confirmation: isConfirm === undefined ? "true" : "false", //выставляем true если изменения приняты или отклонены, false если мы отправляем сообщение об изменениях
			},
		});
		const reviewUrl = process.client
			? new URL(resolvedDealRoute.href, window.location.origin).toString()
			: resolvedDealRoute.href;

		const normalizedReviewUrl = String(await Promise.resolve(reviewUrl));

		let content = "";
		if (isConfirm === true) {
			content = `Изменения заказа ${orderNumber} ПРИНЯТЫ. [Просмотр заказа](${normalizedReviewUrl})`;
		} else if (isConfirm === false) {
			content = `Изменения заказа ${orderNumber} ОТКЛОНЕНЫ. [Просмотр заказа](${normalizedReviewUrl})`;
		} else {
			content = `Изменены условия заказа ${orderNumber}. Пожалуйста, ознакомьтесь с обновлённой версией. [Просмотр заказа](${normalizedReviewUrl})`;
		}

		await sendMessage(chatData.id, {
			content: content,
		});
	}
};