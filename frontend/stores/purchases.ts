import { defineStore } from "pinia";
import type {
  GoodsDeal,
  ServicesDeal,
  EditPersonDeal,
  Services,
  Product,
} from "~/types/dealState";
import { convert as numberToWordsRu } from "number-to-words-ru";

interface Purchases {
  purchases: {
    goodsDeals: GoodsDeal[] | null;
    servicesDeals: ServicesDeal[] | null;
  };
}

export const usePurchasesStore = defineStore("purchases", {
  state: (): Purchases => ({
    purchases: {
      goodsDeals: [
        {
          dealNumber: 7777,
          goods: {
            goodsList: [
              {
                name: "Что-то жесткое",
                article: 33333,
                quantity: 3,
                units: "штуковина",
                price: 33_000,
                amount: 0,
                type: "товар",
              },
            ],
            amountPrice: 0,
            amountWord: "",
            comments: "",
          },
          date: `${new Date().getDate()}.${new Date().getMonth()}.${new Date().getFullYear()}`,
          saller: {
            inn: 7777777,
            name: "Кузя",
            companyName: "Кузя принимает",
            legalAddress: "432 ГВКМЦ",
            mobileNumber: "+77777777",
          },
          buyer: {
            inn: 3423423,
            name: "Sergey",
            companyName: "Home secrets",
            legalAddress: "Minsk, Svisloch river",
            mobileNumber: "+3754445457474",
          },
          state: "в процессе",
          bill: "просмотр",
          supplyContract: "просмотр",
          accompanyingDocuments: "просмотр",
          invoice: "просмотр",
          othersDocuments: "просмотр",
        },
        {
          dealNumber: 666,
          goods: {
            goodsList: [
              {
                name: "Что-то уругое",
                article: 696969,
                quantity: 1,
                units: "штучка",
                price: 69_000,
                amount: 0,
                type: "товар",
              },
            ],
            amountPrice: 0,
            amountWord: "",
            comments: "",
          },
          date: `${new Date().getDate()}.${new Date().getMonth()}.${new Date().getFullYear()}`,
          saller: {
            inn: 6666666,
            name: "Yasha Lava",
            companyName: "DeppAndHard",
            legalAddress: "somewhere",
            mobileNumber: "+23423423433",
          },
          buyer: {
            inn: 3423423,
            name: "Sergey",
            companyName: "Home secrets",
            legalAddress: "Minsk, Svisloch river",
            mobileNumber: "+3754445457474",
          },
          state: "в процессе",
          bill: "просмотр",
          supplyContract: "просмотр",
          accompanyingDocuments: "просмотр",
          invoice: "просмотр",
          othersDocuments: "просмотр",
        },
      ],

      servicesDeals: [
        {
          dealNumber: 666,
          services: {
            servicesList: [
              {
                name: "Что-то уругое",
                article: 696969,
                quantity: 2,
                units: "штучка",
                price: 69_000,
                amount: 0,
                type: "товар",
              },
            ],
            amountPrice: 0,
            amountWord: "",
            comments: "",
          },
          date: `${new Date().getDate()}.${new Date().getMonth()}.${new Date().getFullYear()}`,
          saller: {
            inn: 7777777,
            name: "Yasha Lava",
            companyName: "DeppAndHard",
            legalAddress: "somewhere",
            mobileNumber: "+23423423433",
          },
          buyer: {
            inn: 3423423,
            name: "Sergey",
            companyName: "Home secrets",
            legalAddress: "Minsk, Svisloch river",
            mobileNumber: "+3754445457474",
          },
          state: "в процессе",
          bill: "просмотр",
          contract: "просмотр",
          act: "просмотр",
          invoice: "просмотр",
          othersDocuments: "просмотр",
        },
      ],
    },
  }),

  getters: {
    findGoodsDeal: (state) => {
      return (dealNumber: number) =>
        state.purchases.goodsDeals?.find(
          (deal) => dealNumber === deal.dealNumber
        );
    },

    findServicesDeal: (state) => {
      return (dealNumber: number) =>
        state.purchases.servicesDeals?.find(
          (deal) => dealNumber === deal.dealNumber
        );
    },

    lastGoodsDeal: (state): GoodsDeal | undefined => {
      if (state.purchases.goodsDeals?.[0]) {
        const goodsDeals = state.purchases.goodsDeals;
        const lastDeal = goodsDeals?.[goodsDeals.length - 1];
        return lastDeal;
      }
    },

    lastServiceDeal: (state): ServicesDeal | undefined => {
      if (state.purchases.servicesDeals?.[0]) {
        const servicesDeals = state.purchases.servicesDeals;
        const lastDeal = servicesDeals?.[servicesDeals.length - 1];
        return lastDeal;
      }
    },
  },

  actions: {
    //функция для получения закупок с сервера
    async getPurchases() {},

    amountInGoodsList() {
      this.purchases.goodsDeals?.map((deal) => {
        deal.goods.goodsList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountInServicesList() {
      this.purchases.servicesDeals?.map((deal) => {
        deal.services.servicesList?.map((good) => {
          good.amount = good.price * good.quantity;
        });
      });
    },

    amountPriceInGoods() {
      this.purchases.goodsDeals?.map((deal) => {
        deal.goods.amountPrice = Number(
          deal.goods.goodsList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0
          )
        );
      });
    },

    amountPriceInServices() {
      this.purchases.servicesDeals?.map((deal) => {
        deal.services.amountPrice = Number(
          deal.services.servicesList?.reduce(
            (acc: number, good: Product) => good.amount + acc,
            0
          )
        );
      });
    },

    amountWordGoods() {
      this.purchases.goodsDeals?.map((deal) => {
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
      this.purchases.servicesDeals?.map((deal) => {
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
				const goodsDeals = this.purchases.goodsDeals

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
				const servicesDeals = this.purchases.servicesDeals

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
