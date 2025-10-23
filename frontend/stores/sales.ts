import { defineStore } from "pinia";
import type {
	GoodsDeal,
	ServicesDeal,
	EditPersonDeal,
	Services,
	Product,
} from "~/types/dealState";
import { convert as numberToWordsRu } from "number-to-words-ru";
import { salesGoodsData, salesServiceData } from "~/examples/exampleStoreData";

interface Sales {
	sales: {
		goodsDeals: GoodsDeal[] | null;
		servicesDeals: ServicesDeal[] | null;
	};
}

export const useSalesStore = defineStore("sales", {
	state: (): Sales => ({
		sales: {
			goodsDeals: [
				...salesGoodsData
			],

			servicesDeals: [
				...salesServiceData
			],
		},
	}),

	getters: {
		findGoodsDeal: (state) => {
			return (dealNumber: number) =>
				state.sales.goodsDeals?.find(
					(deal) => dealNumber === deal.dealNumber
				);
		},

		findServicesDeal: (state) => {
			return (dealNumber: number) =>
				state.sales.servicesDeals?.find(
					(deal) => dealNumber === deal.dealNumber
				);
		},

		lastGoodsDeal: (state): GoodsDeal | undefined => {
			if (state.sales.goodsDeals?.[0]) {
				const goodsDeals = state.sales.goodsDeals;
				const lastDeal = goodsDeals?.[goodsDeals.length - 1];
				return lastDeal;
			}
		},

		lastServicesDeal: (state): ServicesDeal | undefined => {
			if (state.sales.servicesDeals?.[0]) {
				const servicesDeals = state.sales.servicesDeals;
				const lastDeal = servicesDeals?.[servicesDeals.length - 1];
				return lastDeal;
			}
		},
	},

	actions: {
		//функция для получения продаж с сервера
		async getPurchases() {},

		amountInGoodsList() {
			this.sales.goodsDeals?.map((deal) => {
				deal.goods.goodsList?.map((good) => {
					good.amount = good.price * good.quantity;
				});
			});
		},

		amountInServicesList() {
			this.sales.servicesDeals?.map((deal) => {
				deal.services.servicesList?.map((good) => {
					good.amount = good.price * good.quantity;
				});
			});
		},

		amountPriceInGoods() {
			this.sales.goodsDeals?.map((deal) => {
				deal.goods.amountPrice = Number(
					deal.goods.goodsList?.reduce(
						(acc: number, good: Product) => good.amount + acc,
						0
					)
				);
			});
		},

		amountPriceInServices() {
			this.sales.servicesDeals?.map((deal) => {
				deal.services.amountPrice = Number(
					deal.services.servicesList?.reduce(
						(acc: number, good: Product) => good.amount + acc,
						0
					)
				);
			});
		},

		amountWordGoods() {
			this.sales.goodsDeals?.map((deal) => {
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

		amountWordServices() {
			this.sales.servicesDeals?.map((deal) => {
				deal.services.amountWord = numberToWordsRu(deal.services.amountPrice, {
					showNumberParts: {
						fractional: false,
					},
					showCurrency: {
						integer: false,
					},
				});
			});
		},

		addNewGood(dealNumber: number, newGood: Product) {
			const goodsList = this.findGoodsDeal(dealNumber)?.goods.goodsList;
			if (goodsList) {
				goodsList.push(newGood);
			}
		},

		addNewService(dealNumber: number, newService: Product) {
			const servicesList =
				this.findServicesDeal(dealNumber)?.services.servicesList;
			if (servicesList) {
				servicesList.push(newService);
			}
		},

		editSallerGoodsDeal(
			dealNumber: number,
			newSallerGoodsDeal: EditPersonDeal
		) {
			const sallerGoodsDeal = this.findGoodsDeal(dealNumber)?.saller;
			if (sallerGoodsDeal) {
				Object.assign(sallerGoodsDeal, newSallerGoodsDeal);
			}
		},

		editSallerServicesDeal(
			dealNumber: number,
			newSallerServicesDeal: EditPersonDeal
		) {
			const sallerServicesDeal = this.findServicesDeal(dealNumber)?.saller;
			if (sallerServicesDeal) {
				Object.assign(sallerServicesDeal, newSallerServicesDeal);
			}
		},

		editBuyerGoodsDeal(dealNumber: number, newSallerGoodsDeal: EditPersonDeal) {
			const buyerGoodsDeal = this.findGoodsDeal(dealNumber)?.buyer;
			if (buyerGoodsDeal) {
				Object.assign(buyerGoodsDeal, newSallerGoodsDeal);
			}
		},

		editBuyerServicesDeal(
			dealNumber: number,
			newSallerServicesDeal: EditPersonDeal
		) {
			const buyerServicesDeal = this.findServicesDeal(dealNumber)?.buyer;
			if (buyerServicesDeal) {
				Object.assign(buyerServicesDeal, newSallerServicesDeal);
			}
		},

		editGood(dealNumber: number, newGoodsList: Product[]) {
			const goodsDeal = this.findGoodsDeal(dealNumber)
			if (goodsDeal) {
				goodsDeal.goods.goodsList = [...newGoodsList]
			}
		},

		editService(dealNumber: number, newServiceList: Product[]) {
			const serviceDeal = this.findServicesDeal(dealNumber)
			if (serviceDeal) {
				serviceDeal.services.servicesList = [...newServiceList]
			}
		},

		editGoodsComments(dealNumber: number, comments: string) {
			const goods = this.findGoodsDeal(dealNumber)?.goods;
			if (goods) {
				goods.comments = comments;
			}
		},

		editServicesComments(dealNumber: number, comments: string) {
			const goods = this.findServicesDeal(dealNumber)?.services;
			if (goods) {
				goods.comments = comments;
			}
		},

		removeGoodsDeal(dealNumber: number) {
			if (dealNumber) {
				const goodsDeal = this.findGoodsDeal(dealNumber);
				const goodsDeals = this.sales.goodsDeals

				if (goodsDeal) {
					const index = goodsDeals?.findIndex((goods: GoodsDeal) => {
						return goods.dealNumber === goodsDeal.dealNumber;
					});

					if (index !== -1 && typeof (index) !== 'undefined') {
						goodsDeals?.splice(index, 1);
					}
				}
			}
		},

		removeServicesDeal(dealNumber: number) {
			if (dealNumber) {
				const servicesDeal = this.findServicesDeal(dealNumber);
				const servicesDeals = this.sales.servicesDeals

				if (servicesDeal) {
					const index = servicesDeals?.findIndex((service: ServicesDeal) => {
						return service.dealNumber === servicesDeal.dealNumber;
					});

					if (index !== -1 && typeof (index) !== 'undefined') {
						servicesDeals?.splice(index, 1);
					}
				}
			}
		},
	},
});
