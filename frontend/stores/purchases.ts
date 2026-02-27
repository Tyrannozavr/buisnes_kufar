import { defineStore } from "pinia";
import type { GoodsDeal, EditPersonDeal, Product } from "~/types/dealState";
import type {
	BuyerDealResponse,
	DealUpdate,
	OrderItemUpdate,
} from "~/types/dealResponse";
import numberToWordsRuPkg from "number-to-words-ru";
const numberToWordsRu = numberToWordsRuPkg.convert;
import type { PurchasesApi } from "~/api/purchases";

interface Purchases {
	purchases: {
		goodsDeals: GoodsDeal[];
	};
}

export const usePurchasesStore = defineStore("purchases", {
	state: (): Purchases => ({
		purchases: {
			goodsDeals: [],
		},
	}),

	getters: {
		findGoodsDealByDealNumber: (state) => {
			return (dealNumber: string) =>
				state.purchases.goodsDeals?.find(
					(deal) => dealNumber === deal.buyerOrderNumber,
				);
		},

		findGoodsDeal: (state) => {
			return (dealId: number) =>
				state.purchases.goodsDeals?.find((deal) => dealId === deal.dealId);
		},

		lastGoodsDeal: (state): GoodsDeal | undefined => {
			if (state.purchases.goodsDeals?.[0]) {
				const goodsDeals = state.purchases.goodsDeals;
				let maxDealId = 0;
				goodsDeals?.forEach((deal) => {
					if (deal.dealId > maxDealId) {
						maxDealId = deal.dealId;
					}
				});

				const lastDeal = state.purchases.goodsDeals?.find(
					(deal) => deal.dealId === maxDealId,
				);

				return lastDeal;
			}
		},

		createBodyForUpdate:
			(state) =>
			(orderId: number): DealUpdate | null => {
				const deal: GoodsDeal | undefined =
					state.purchases.goodsDeals?.find((d) => d.dealId === orderId);

				if (!deal) return null;

				const products = deal.goods.goodsList;

				const itemsList: OrderItemUpdate[] = (products ?? []).map((p) => ({
					product_name: p.name?.trim() || "—",
					quantity: p.quantity,
					unit_of_measurement: p.units?.trim() || "шт",
					price: p.price,
				}));

				const body: DealUpdate = {
					items: itemsList,
					comments: deal.goods.comments ?? undefined,
				};
				if (deal.status) body.status = deal.status;
				if (deal.contractNumber) body.contract_number = deal.contractNumber;
				if (deal.billNumber) body.bill_number = deal.billNumber;
				if (deal.supplyContractNumber)
					body.supply_contracts_number = deal.supplyContractNumber;
				return body;
			},
	},

	actions: {
		async clearStore() {
			this.purchases.goodsDeals = [];
		},

		//получение и заполнение списка сделок
		async getDeals(api: PurchasesApi) {
			await this.clearStore();

			const { getDealById, getBuyerDeals } = api;
			const buyerDeals = await getBuyerDeals();
			const dealsIds: number[] = [
				...new Set(
					(buyerDeals?.map((deal: BuyerDealResponse) => deal.id) ?? []) as number[],
				),
			];

			//функция для преобразования данных и заполнения списка сделок
			const fillDeals = async (dealId: number) => {
				const dealResponse = await getDealById(dealId);
				if (!dealResponse) return;

				this.addNewGoodsDeal({
					dealId: dealResponse.id,
					buyerOrderNumber: dealResponse.buyer_order_number,
					sellerOrderNumber: dealResponse.seller_order_number,
					date: dealResponse.created_at,
					goods: {
						goodsList: dealResponse.items.map((item: any) => ({
							name: item.product_name,
							article: item.product_article,
							quantity: item.quantity,
							units: item.unit_of_measurement,
							price: item.price,
							amount: item.amount,
						})),
						amountPrice: 0,
						amountWord: "",
						comments: dealResponse.comments ?? "",
					},
					seller: {
						sellerName: dealResponse.seller_company.name,
						companyName: dealResponse.seller_company.company_name,
						phone: dealResponse.seller_company.phone,
						slug: dealResponse.seller_company.slug,
						companyId: dealResponse.seller_company.id,
						email: dealResponse.seller_company.email,
						inn: dealResponse.seller_company.inn,
						legalAddress: dealResponse.seller_company.legal_address,
					},
					buyer: {
						buyerName: dealResponse.buyer_company.name,
						companyName: dealResponse.buyer_company.company_name,
						phone: dealResponse.buyer_company.phone,
						slug: dealResponse.buyer_company.slug,
						companyId: dealResponse.buyer_company.id,
						email: dealResponse.buyer_company.email,
						inn: dealResponse.buyer_company.inn,
						legalAddress: dealResponse.buyer_company.legal_address,
					},
					status: dealResponse.status,
					billNumber: dealResponse.bill_number || "",
					billDate: dealResponse.bill_date || "",
					contractNumber: dealResponse.contract_number || "",
					contractDate: dealResponse.contract_date || "",
					supplyContractNumber: dealResponse.supply_contracts_number || "",
					supplyContractDate: dealResponse.supply_contracts_date || "",
					closingDocuments: dealResponse.closing_documents || [],
					othersDocuments: dealResponse.others_documents || [],
				});
			};

			//заполнение списка сделок
			for (const dealId of dealsIds) {
				await fillDeals(dealId);
			}
		},

		async createNewDealVersion(dealId: number, api: PurchasesApi) {
			const { createNewDealVersion } = api;
			const body = this.createBodyForUpdate(dealId);
			await createNewDealVersion(dealId, body ?? {});
		},

		addNewGoodsDeal(newDeal: GoodsDeal) {
			if (!newDeal) return;
			const exists = this.purchases.goodsDeals?.some(
				(d) => d.dealId === newDeal.dealId,
			);
			if (!exists) {
				this.purchases.goodsDeals?.push(newDeal);
			}
		},

		amountInGoodsList() {
			this.purchases.goodsDeals?.forEach((deal) => {
				deal.goods.goodsList?.forEach((good) => {
					good.amount = good.price * good.quantity;
				});
			});
		},

		amountPriceInGoods() {
			this.purchases.goodsDeals?.forEach((deal) => {
				deal.goods.amountPrice = Number(
					deal.goods.goodsList?.reduce(
						(acc: number, good: Product) => good.amount + acc,
						0,
					),
				);
			});
		},

		amountWordGoods() {
			this.purchases.goodsDeals?.forEach((deal) => {
				deal.goods.amountWord = numberToWordsRu(deal.goods.amountPrice, {
					showNumberParts: {
						fractional: false,
					},
					showCurrency: {
						integer: false,
					},
				});
			});
		},

		addNewGood(dealId: number, newGood: Product) {
			const goodsList = this.findGoodsDeal(dealId)?.goods.goodsList;
			if (goodsList) {
				goodsList.push(newGood);
			}
		},

		editSellerGoodsDeal(dealId: number, newSellerGoodsDeal: EditPersonDeal) {
			const sellerGoodsDeal = this.findGoodsDeal(dealId)?.seller;
			if (sellerGoodsDeal) {
				Object.assign(sellerGoodsDeal, newSellerGoodsDeal);
			}
		},

		editBuyerGoodsDeal(dealId: number, newBuyerGoodsDeal: EditPersonDeal) {
			const buyerGoodsDeal = this.findGoodsDeal(dealId)?.buyer;
			if (buyerGoodsDeal) {
				Object.assign(buyerGoodsDeal, newBuyerGoodsDeal);
			}
		},

		editGood(dealId: number, newGoodsList: Product[]) {
			const goodsDeal = this.findGoodsDeal(dealId);
			if (goodsDeal) {
				goodsDeal.goods.goodsList = [...newGoodsList];
			}
		},

		editGoodsComments(dealId: number, comments: string) {
			const goods = this.findGoodsDeal(dealId)?.goods;
			if (goods) {
				goods.comments = comments;
			}
		},

		removeGoodsDeal(dealId: number, api: PurchasesApi) {
			if (!dealId) return;

			const goodsDeal = this.findGoodsDeal(dealId);
			const goodsDeals = this.purchases.goodsDeals;
			const { deleteDealById } = api;

			if (!goodsDeal) return;

			const index = goodsDeals?.findIndex((goods: GoodsDeal) => {
				return goods.dealId === goodsDeal.dealId;
			});

			if (index !== -1 && typeof index !== "undefined") {
				goodsDeals?.splice(index, 1);
				deleteDealById(dealId);
			}
		},

		async fullUpdateGoodsDeal(
			dealId: number,
			seller: EditPersonDeal,
			buyer: EditPersonDeal,
			newGoodsList: Product[],
			api: PurchasesApi,
			comments?: string,
		) {
			this.amountInGoodsList();
			this.amountPriceInGoods();
			this.amountWordGoods();
			this.editSellerGoodsDeal(dealId, seller);
			this.editBuyerGoodsDeal(dealId, buyer);
			this.editGood(dealId, newGoodsList);
			if (comments !== undefined) {
				this.editGoodsComments(dealId, comments);
			}

			const { updateDealById } = api;
			const body = this.createBodyForUpdate(dealId);
			if (body) {
				await updateDealById(dealId, body);
			}
		},
	},
});
